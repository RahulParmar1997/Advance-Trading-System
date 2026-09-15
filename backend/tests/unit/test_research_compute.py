import pytest

from advance_system.research.compute import (
    ComputeBackend,
    LocalResearchExecutor,
    ResearchStatus,
    ResourceLimits,
    ResearchJob,
)


def job(**overrides: object) -> ResearchJob:
    values = {
        "dataset_version": "dataset-v1",
        "strategy_version": "strategy-v1",
        "feature_version": "features-v1",
        "configuration_version": "config-v1",
        "git_commit_sha": "a" * 40,
        "random_seed": 7,
    }
    values.update(overrides)
    return ResearchJob.create(**values)


def test_research_job_records_reproducibility_metadata() -> None:
    research_job = job(backend=ComputeBackend.LOCAL_CPU)

    assert research_job.job_id is not None
    assert research_job.status is ResearchStatus.RAW
    assert research_job.git_commit_sha == "a" * 40
    assert research_job.random_seed == 7


def test_local_executor_moves_job_to_computed_without_execution_authority() -> None:
    research_job = LocalResearchExecutor().submit(job())

    assert research_job.status is ResearchStatus.COMPUTED
    assert research_job.backend is ComputeBackend.LOCAL_CPU


def test_local_executor_rejects_remote_backend() -> None:
    with pytest.raises(ValueError, match="local compute backends"):
        LocalResearchExecutor().submit(job(backend=ComputeBackend.CLOUD_HPC))


def test_resource_limits_fail_closed() -> None:
    with pytest.raises(ValueError, match="max_seconds"):
        ResourceLimits(max_seconds=0).validate()
    with pytest.raises(ValueError, match="max_concurrency"):
        ResourceLimits(max_concurrency=0).validate()
    with pytest.raises(ValueError, match="max_storage_bytes"):
        ResourceLimits(max_storage_bytes=0).validate()


def test_job_requires_reproducibility_metadata() -> None:
    with pytest.raises(ValueError, match="dataset_version"):
        job(dataset_version="")
    with pytest.raises(ValueError, match="random_seed"):
        job(random_seed=-1)
