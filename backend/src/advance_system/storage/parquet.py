from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from urllib.parse import urlparse

from advance_system.storage.contracts import StorageConfig

_PATH_PART = re.compile(r"^[A-Za-z0-9._-]+$")
_PARTITION_PART = re.compile(r"^[A-Za-z0-9._=-]+$")


class ObjectStore(Protocol):
    """Minimal object boundary; concrete cloud SDKs stay outside the domain."""

    async def exists(self, key: str) -> bool:
        ...

    async def read(self, key: str) -> bytes:
        ...

    async def write_if_absent(self, key: str, payload: bytes) -> bool:
        """Write only when absent and return whether a new object was created."""
        ...

    async def healthcheck(self) -> bool:
        ...


@dataclass(frozen=True, slots=True)
class ResearchDatasetRef:
    """Immutable address of one versioned research dataset partition."""

    dataset: str
    version: str
    partition: str = "default"

    def validate(self) -> None:
        if not self.dataset or not _PATH_PART.fullmatch(self.dataset):
            raise ValueError("invalid dataset")
        if not self.version or not _PATH_PART.fullmatch(self.version):
            raise ValueError("invalid version")
        if not self.partition or not _PARTITION_PART.fullmatch(self.partition):
            raise ValueError("invalid partition")


@dataclass(frozen=True, slots=True)
class DatasetManifest:
    """Content-addressed metadata for an immutable dataset payload."""

    dataset: str
    version: str
    partition: str
    sha256: str
    size_bytes: int
    created_at: datetime
    immutable: bool = True

    def validate(self) -> None:
        if len(self.sha256) != 64 or any(char not in "0123456789abcdef" for char in self.sha256):
            raise ValueError("sha256 must be a lowercase SHA-256 hex digest")
        if self.size_bytes < 0 or not self.immutable:
            raise ValueError("dataset manifest must be immutable with a non-negative size")
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")

    def to_bytes(self) -> bytes:
        self.validate()
        payload = {
            "dataset": self.dataset,
            "version": self.version,
            "partition": self.partition,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at.astimezone(timezone.utc).isoformat(),
            "immutable": self.immutable,
        }
        return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


class ImmutableParquetStore:
    """Versioned Parquet/object store with append-only, fail-closed semantics."""

    def __init__(self, config: StorageConfig, object_store: ObjectStore) -> None:
        config.validate()
        if not urlparse(config.parquet_root).scheme:
            raise ValueError("parquet_root must be a filesystem or object-storage URI")
        self._root = config.parquet_root.rstrip("/")
        self._object_store = object_store

    async def write_dataset(
        self, ref: ResearchDatasetRef, payload: bytes, *, created_at: datetime | None = None
    ) -> DatasetManifest:
        ref.validate()
        if not isinstance(payload, bytes):
            raise TypeError("Parquet payload must be bytes")
        if not payload:
            raise ValueError("Parquet payload cannot be empty")
        if not payload.startswith(b"PAR1"):
            raise ValueError("payload must be a Parquet file")

        timestamp = created_at or datetime.now(timezone.utc)
        digest = hashlib.sha256(payload).hexdigest()
        manifest = DatasetManifest(ref.dataset, ref.version, ref.partition, digest, len(payload), timestamp)
        manifest.validate()
        data_key = self._key(ref, "data.parquet")
        manifest_key = self._key(ref, "manifest.json")

        if await self._object_store.exists(data_key) or await self._object_store.exists(manifest_key):
            existing_manifest = await self._read_manifest(manifest_key)
            if existing_manifest.sha256 != digest or existing_manifest.size_bytes != len(payload):
                raise ValueError("immutable dataset version already exists with different content")
            existing_payload = await self._object_store.read(data_key)
            if hashlib.sha256(existing_payload).hexdigest() != digest:
                raise ValueError("dataset content hash does not match its manifest")
            return existing_manifest

        created = await self._object_store.write_if_absent(data_key, payload)
        if not created:
            existing_manifest = await self._read_manifest(manifest_key)
            if existing_manifest.sha256 != digest:
                raise ValueError("immutable dataset version already exists with different content")
            return existing_manifest

        manifest_created = await self._object_store.write_if_absent(manifest_key, manifest.to_bytes())
        if not manifest_created:
            existing_manifest = await self._read_manifest(manifest_key)
            if existing_manifest.sha256 != digest:
                raise ValueError("immutable dataset version already exists with different content")
            return existing_manifest
        return manifest

    async def read_dataset(self, ref: ResearchDatasetRef) -> bytes:
        ref.validate()
        manifest = await self._read_manifest(self._key(ref, "manifest.json"))
        payload = await self._object_store.read(self._key(ref, "data.parquet"))
        if len(payload) != manifest.size_bytes or hashlib.sha256(payload).hexdigest() != manifest.sha256:
            raise ValueError("dataset payload failed manifest integrity check")
        return payload

    async def read_manifest(self, ref: ResearchDatasetRef) -> DatasetManifest:
        ref.validate()
        return await self._read_manifest(self._key(ref, "manifest.json"))

    async def healthcheck(self) -> bool:
        try:
            return await self._object_store.healthcheck()
        except Exception:
            return False

    async def _read_manifest(self, key: str) -> DatasetManifest:
        raw = await self._object_store.read(key)
        try:
            data = json.loads(raw.decode("utf-8"))
            manifest = DatasetManifest(
                dataset=data["dataset"],
                version=data["version"],
                partition=data["partition"],
                sha256=data["sha256"],
                size_bytes=data["size_bytes"],
                created_at=datetime.fromisoformat(data["created_at"]),
                immutable=data["immutable"],
            )
            manifest.validate()
            return manifest
        except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid dataset manifest") from exc

    def _key(self, ref: ResearchDatasetRef, name: str) -> str:
        ref.validate()
        return (
            f"{self._root}/dataset={ref.dataset}/version={ref.version}/"
            f"partition={ref.partition}/{name}"
        )


ParquetStoreAdapter = ImmutableParquetStore
