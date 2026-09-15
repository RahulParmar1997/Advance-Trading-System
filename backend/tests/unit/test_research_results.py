from dataclasses import replace
from datetime import datetime, timezone

import pytest

from advance_system.research.compute import ComputeBackend, ResearchJob, ResearchStatus, ResourceLimits
from advance_system.research.results import (
    EnvironmentMetadata,
    HardwareMetadata,
    InMemoryResearchResultStore,
    ResearchResultManifest,
    ResourceUsage,
)


NOW = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)


def computed_job(**kwargs: object) -> ResearchJob:
    return ResearchJob(
        job_id=ResearchJob.create(
            dataset_version="dataset-v1",
            strategy_version="strategy-v1",
            feature_version="features-v1",
            configuration_version="config-v1",
            git_commit_sha="a" * 40,
            random_seed=7,
        ).job_id,
        dataset_version="dataset-v1",
        strategy_version="strategy-v1",
        feature_version="features-v1",
        configuration_version="config-v1",
        git_commit_sha="a" * 40,
        random_seed=7,
        backend=ComputeBackend.LOCAL_CPU,
        status=ResearchStatus.COMPUTED,
        resource_limits=ResourceLimits(**kwargs),
    )


def metadata() -> tuple[HardwareMetadata, EnvironmentMetadata, ResourceUsage]:
    return (
        HardwareMetadata(cpu="actual-cpu", gpu=None, worker_count=1),
        EnvironmentMetadata(os="Linux", python="3.11.9", runtime="pytest"),
        ResourceUsage(elapsed_seconds=3, storage_bytes=11, concurrency=1),
    )


def manifest_for(job: ResearchJob, result: bytes = b"test-result") -> ResearchResultManifest:
    hardware, environment, usage = metadata()
    return ResearchResultManifest.from_job(
        job,
        result,
        hardware=hardware,
        environment=environment,
        resource_usage=usage,
        created_at=NOW,
    )


def test_manifest_records_canonical_checksum_and_provenance() -> None:
    result = b"test-result"
    manifest = manifest_for(computed_job(), result)

    assert manifest.result_sha256 == "b1dc7b8ec52f50b8e8a7ffc1adbccbb08fe7cad5cbb7a2bdeec9c75ca61065a4"
    assert manifest.result_size_bytes == len(result)
    assert manifest.status is ResearchStatus.COMPUTED
    assert manifest.created_at.tzinfo is not None


def test_manifest_rejects_missing_hardware_or_environment() -> None:
    job = computed_job()
    hardware, environment, usage = metadata()

    with pytest.raises(ValueError, match="hardware cpu"):
        ResearchResultManifest.from_job(
            job,
            b"result",
            hardware=HardwareMetadata(cpu=""),
            environment=environment,
            resource_usage=usage,
            created_at=NOW,
        )

    with pytest.raises(ValueError, match="environment metadata"):
        ResearchResultManifest.from_job(
            job,
            b"result",
            hardware=hardware,
            environment=EnvironmentMetadata(os="", python="3.11", runtime="pytest"),
            resource_usage=usage,
            created_at=NOW,
        )


def test_manifest_rejects_resource_limit_breach() -> None:
    job = computed_job(max_seconds=2, max_concurrency=1, max_storage_bytes=3)
    hardware, environment, _ = metadata()

    with pytest.raises(ValueError, match="max_seconds"):
        ResearchResultManifest.from_job(
            job,
            b"result",
            hardware=hardware,
            environment=environment,
            resource_usage=ResourceUsage(elapsed_seconds=3, storage_bytes=6, concurrency=1),
            created_at=NOW,
        )


@pytest.mark.asyncio
async def test_store_is_write_once_and_integrity_checked() -> None:
    store = InMemoryResearchResultStore()
    job = computed_job(max_storage_bytes=100)
    manifest = manifest_for(job, b"result")

    await store.write(manifest, b"result")
    with pytest.raises(ValueError, match="already exists"):
        await store.write(manifest, b"result")
    with pytest.raises(ValueError, match="checksum"):
        await store.write(replace(manifest, result_sha256="0" * 64), b"result")

    stored_manifest, stored_result = await store.read(job.job_id)
    assert stored_manifest == manifest
    assert stored_result == b"result"


def test_result_persistence_never_promotes_research_status() -> None:
    manifest = manifest_for(computed_job())
    assert manifest.status is ResearchStatus.COMPUTED
    with pytest.raises(ValueError, match="COMPUTED"):
        replace(manifest, status=ResearchStatus.RESEARCH_APPROVED).validate()
