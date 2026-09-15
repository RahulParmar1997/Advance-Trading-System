from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID

from advance_system.research.compute import ComputeBackend, ResearchJob, ResearchStatus
from advance_system.storage.parquet import ObjectStore


@dataclass(frozen=True, slots=True)
class HardwareMetadata:
    """Observed worker hardware identity supplied by the actual executor."""

    cpu: str
    gpu: str | None = None
    worker_count: int = 1

    def validate(self) -> None:
        if not self.cpu:
            raise ValueError("hardware cpu is required")
        if self.worker_count <= 0:
            raise ValueError("hardware worker_count must be positive")


@dataclass(frozen=True, slots=True)
class EnvironmentMetadata:
    """Observed execution environment identity; values are never inferred here."""

    os: str
    python: str
    runtime: str

    def validate(self) -> None:
        if not self.os or not self.python or not self.runtime:
            raise ValueError("environment metadata is required")


@dataclass(frozen=True, slots=True)
class ResourceUsage:
    """Observed resource consumption for one completed research result."""

    elapsed_seconds: int
    storage_bytes: int
    concurrency: int

    def validate(self) -> None:
        if self.elapsed_seconds < 0:
            raise ValueError("elapsed_seconds must be non-negative")
        if self.storage_bytes < 0:
            raise ValueError("storage_bytes must be non-negative")
        if self.concurrency <= 0:
            raise ValueError("concurrency must be positive")


@dataclass(frozen=True, slots=True)
class ResearchResultManifest:
    """Immutable, content-addressed provenance for a computed research result."""

    job_id: UUID
    dataset_version: str
    strategy_version: str
    feature_version: str
    configuration_version: str
    git_commit_sha: str
    random_seed: int
    backend: ComputeBackend
    status: ResearchStatus
    result_sha256: str
    result_size_bytes: int
    hardware: HardwareMetadata
    environment: EnvironmentMetadata
    resource_usage: ResourceUsage
    created_at: datetime

    def validate(self) -> None:
        if self.status is not ResearchStatus.COMPUTED:
            raise ValueError("research result must be persisted at COMPUTED status")
        if len(self.result_sha256) != 64 or any(
            char not in "0123456789abcdef" for char in self.result_sha256
        ):
            raise ValueError("result_sha256 must be a lowercase SHA-256 hex digest")
        if self.result_size_bytes < 0:
            raise ValueError("result_size_bytes must be non-negative")
        if self.random_seed < 0:
            raise ValueError("random_seed must be non-negative")
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        for name, value in (
            ("dataset_version", self.dataset_version),
            ("strategy_version", self.strategy_version),
            ("feature_version", self.feature_version),
            ("configuration_version", self.configuration_version),
            ("git_commit_sha", self.git_commit_sha),
        ):
            if not value:
                raise ValueError(f"{name} is required")
        self.hardware.validate()
        self.environment.validate()
        self.resource_usage.validate()

    @classmethod
    def from_job(
        cls,
        job: ResearchJob,
        result: bytes,
        *,
        hardware: HardwareMetadata,
        environment: EnvironmentMetadata,
        resource_usage: ResourceUsage,
        created_at: datetime,
    ) -> ResearchResultManifest:
        job.validate()
        if job.status is not ResearchStatus.COMPUTED:
            raise ValueError("research job must be COMPUTED before result persistence")
        if not isinstance(result, bytes) or not result:
            raise ValueError("research result must be non-empty bytes")
        hardware.validate()
        environment.validate()
        resource_usage.validate()
        if resource_usage.elapsed_seconds > job.resource_limits.max_seconds:
            raise ValueError("research result exceeded max_seconds")
        if resource_usage.concurrency > job.resource_limits.max_concurrency:
            raise ValueError("research result exceeded max_concurrency")
        if resource_usage.storage_bytes > job.resource_limits.max_storage_bytes:
            raise ValueError("research result exceeded max_storage_bytes")
        manifest = cls(
            job_id=job.job_id,
            dataset_version=job.dataset_version,
            strategy_version=job.strategy_version,
            feature_version=job.feature_version,
            configuration_version=job.configuration_version,
            git_commit_sha=job.git_commit_sha,
            random_seed=job.random_seed,
            backend=job.backend,
            status=ResearchStatus.COMPUTED,
            result_sha256=hashlib.sha256(result).hexdigest(),
            result_size_bytes=len(result),
            hardware=hardware,
            environment=environment,
            resource_usage=resource_usage,
            created_at=created_at,
        )
        manifest.validate()
        if resource_usage.storage_bytes < manifest.result_size_bytes:
            raise ValueError("resource storage_bytes cannot be smaller than result size")
        return manifest

    def to_bytes(self) -> bytes:
        self.validate()
        payload = {
            "job_id": str(self.job_id),
            "dataset_version": self.dataset_version,
            "strategy_version": self.strategy_version,
            "feature_version": self.feature_version,
            "configuration_version": self.configuration_version,
            "git_commit_sha": self.git_commit_sha,
            "random_seed": self.random_seed,
            "backend": self.backend.value,
            "status": self.status.value,
            "result_sha256": self.result_sha256,
            "result_size_bytes": self.result_size_bytes,
            "hardware": {
                "cpu": self.hardware.cpu,
                "gpu": self.hardware.gpu,
                "worker_count": self.hardware.worker_count,
            },
            "environment": {
                "os": self.environment.os,
                "python": self.environment.python,
                "runtime": self.environment.runtime,
            },
            "resource_usage": {
                "elapsed_seconds": self.resource_usage.elapsed_seconds,
                "storage_bytes": self.resource_usage.storage_bytes,
                "concurrency": self.resource_usage.concurrency,
            },
            "created_at": self.created_at.astimezone(timezone.utc).isoformat(),
        }
        return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> ResearchResultManifest:
        try:
            data = json.loads(raw.decode("utf-8"))
            manifest = cls(
                job_id=UUID(data["job_id"]),
                dataset_version=data["dataset_version"],
                strategy_version=data["strategy_version"],
                feature_version=data["feature_version"],
                configuration_version=data["configuration_version"],
                git_commit_sha=data["git_commit_sha"],
                random_seed=data["random_seed"],
                backend=ComputeBackend(data["backend"]),
                status=ResearchStatus(data["status"]),
                result_sha256=data["result_sha256"],
                result_size_bytes=data["result_size_bytes"],
                hardware=HardwareMetadata(**data["hardware"]),
                environment=EnvironmentMetadata(**data["environment"]),
                resource_usage=ResourceUsage(**data["resource_usage"]),
                created_at=datetime.fromisoformat(data["created_at"]),
            )
            manifest.validate()
            return manifest
        except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid research result manifest") from exc


class ResearchResultStore(Protocol):
    async def write(self, manifest: ResearchResultManifest, result: bytes) -> None:
        """Persist a computed result without overwrite or execution authority."""

    async def read(self, job_id: UUID) -> tuple[ResearchResultManifest, bytes]:
        """Read and integrity-check an immutable research result."""


class InMemoryResearchResultStore:
    """Deterministic write-once store used to exercise the immutable boundary."""

    def __init__(self) -> None:
        self._results: dict[UUID, tuple[ResearchResultManifest, bytes]] = {}

    async def write(self, manifest: ResearchResultManifest, result: bytes) -> None:
        manifest.validate()
        if not isinstance(result, bytes) or not result:
            raise ValueError("research result must be non-empty bytes")
        if hashlib.sha256(result).hexdigest() != manifest.result_sha256:
            raise ValueError("research result checksum does not match manifest")
        if len(result) != manifest.result_size_bytes:
            raise ValueError("research result size does not match manifest")
        if manifest.job_id in self._results:
            raise ValueError("research result already exists and is immutable")
        self._results[manifest.job_id] = (manifest, bytes(result))

    async def read(self, job_id: UUID) -> tuple[ResearchResultManifest, bytes]:
        try:
            manifest, result = self._results[job_id]
        except KeyError as exc:
            raise KeyError("research result not found") from exc
        if hashlib.sha256(result).hexdigest() != manifest.result_sha256:
            raise ValueError("stored research result failed checksum validation")
        if len(result) != manifest.result_size_bytes:
            raise ValueError("stored research result failed size validation")
        return manifest, bytes(result)


class ObjectStoreResearchResultStore:
    """Concrete immutable research-result persistence over the existing ObjectStore boundary."""

    def __init__(self, object_store: ObjectStore, *, root: str = "research-results") -> None:
        if not root or root.strip("/") != root or "//" in root:
            raise ValueError("research result root must be a non-empty relative object prefix")
        self._object_store = object_store
        self._root = root

    async def write(self, manifest: ResearchResultManifest, result: bytes) -> None:
        manifest.validate()
        if not isinstance(result, bytes) or not result:
            raise ValueError("research result must be non-empty bytes")
        if hashlib.sha256(result).hexdigest() != manifest.result_sha256:
            raise ValueError("research result checksum does not match manifest")
        if len(result) != manifest.result_size_bytes:
            raise ValueError("research result size does not match manifest")

        result_key = self._key(manifest.job_id, "result.bin")
        manifest_key = self._key(manifest.job_id, "manifest.json")
        created = await self._object_store.write_if_absent(result_key, bytes(result))
        if not created:
            existing = await self._object_store.read(result_key)
            if hashlib.sha256(existing).hexdigest() != manifest.result_sha256 or len(existing) != manifest.result_size_bytes:
                raise ValueError("immutable research result already exists with different content")

        manifest_created = await self._object_store.write_if_absent(manifest_key, manifest.to_bytes())
        if not manifest_created:
            existing_manifest = ResearchResultManifest.from_bytes(await self._object_store.read(manifest_key))
            if existing_manifest != manifest:
                raise ValueError("immutable research result already exists with different manifest")

    async def read(self, job_id: UUID) -> tuple[ResearchResultManifest, bytes]:
        manifest = ResearchResultManifest.from_bytes(
            await self._object_store.read(self._key(job_id, "manifest.json"))
        )
        result = await self._object_store.read(self._key(job_id, "result.bin"))
        if hashlib.sha256(result).hexdigest() != manifest.result_sha256:
            raise ValueError("stored research result failed checksum validation")
        if len(result) != manifest.result_size_bytes:
            raise ValueError("stored research result failed size validation")
        return manifest, bytes(result)

    async def healthcheck(self) -> bool:
        try:
            return await self._object_store.healthcheck()
        except Exception:
            return False

    def _key(self, job_id: UUID, name: str) -> str:
        return f"{self._root}/job={job_id}/{name}"
