from __future__ import annotations

from datetime import datetime, timezone

import pytest

from advance_system.storage.contracts import StorageConfig
from advance_system.storage.parquet import ImmutableParquetStore, ResearchDatasetRef


class FakeObjectStore:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def exists(self, key: str) -> bool:
        return key in self.objects

    async def read(self, key: str) -> bytes:
        return self.objects[key]

    async def write_if_absent(self, key: str, payload: bytes) -> bool:
        if key in self.objects:
            return False
        self.objects[key] = payload
        return True

    async def healthcheck(self) -> bool:
        return True


def config() -> StorageConfig:
    return StorageConfig(
        postgres_dsn="postgresql://db.example/ats",
        clickhouse_dsn="https://analytics.example",
        redis_url="redis://cache.example/0",
        parquet_root="s3://ats-research",
    )


def ref() -> ResearchDatasetRef:
    return ResearchDatasetRef("features", "v1", "date=2026-09-15")


@pytest.mark.asyncio
async def test_parquet_write_read_and_manifest_are_content_addressed() -> None:
    backend = FakeObjectStore()
    store = ImmutableParquetStore(config(), backend)
    payload = b"PAR1research-data"
    created_at = datetime(2026, 9, 15, tzinfo=timezone.utc)

    manifest = await store.write_dataset(ref(), payload, created_at=created_at)
    assert manifest.sha256
    assert manifest.size_bytes == len(payload)
    assert manifest.created_at == created_at
    assert await store.read_dataset(ref()) == payload
    assert await store.read_manifest(ref()) == manifest
    assert "dataset=features/version=v1/partition=date=2026-09-15/data.parquet" in backend.objects


@pytest.mark.asyncio
async def test_same_version_same_content_is_idempotent() -> None:
    backend = FakeObjectStore()
    store = ImmutableParquetStore(config(), backend)
    payload = b"PAR1same"

    first = await store.write_dataset(ref(), payload)
    second = await store.write_dataset(ref(), payload)

    assert second == first
    assert len(backend.objects) == 2


@pytest.mark.asyncio
async def test_same_version_different_content_is_rejected() -> None:
    backend = FakeObjectStore()
    store = ImmutableParquetStore(config(), backend)
    await store.write_dataset(ref(), b"PAR1first")

    with pytest.raises(ValueError, match="different content"):
        await store.write_dataset(ref(), b"PAR1second")


@pytest.mark.asyncio
async def test_dataset_ref_rejects_path_traversal() -> None:
    backend = FakeObjectStore()
    store = ImmutableParquetStore(config(), backend)

    with pytest.raises(ValueError, match="invalid dataset"):
        await store.write_dataset(ResearchDatasetRef("../orders", "v1"), b"PAR1x")
    with pytest.raises(ValueError, match="invalid version"):
        await store.write_dataset(ResearchDatasetRef("features", "../v2"), b"PAR1x")


@pytest.mark.asyncio
async def test_parquet_payload_is_required() -> None:
    backend = FakeObjectStore()
    store = ImmutableParquetStore(config(), backend)

    with pytest.raises(ValueError, match="Parquet file"):
        await store.write_dataset(ref(), b"not-parquet")
