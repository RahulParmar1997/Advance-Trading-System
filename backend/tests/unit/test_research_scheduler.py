from advance_system.research.compute import ComputeBackend, ResearchJob
from advance_system.research.scheduler import (
    CloudHPCAdapter,
    DistributedCPUAdapter,
    DistributedGPUAdapter,
)


def job(backend: ComputeBackend) -> ResearchJob:
    return ResearchJob.create(
        dataset_version="dataset-v1",
        strategy_version="strategy-v1",
        feature_version="features-v1",
        configuration_version="config-v1",
        git_commit_sha="a" * 40,
        random_seed=7,
        backend=backend,
    )


def test_distributed_adapters_enqueue_without_marking_job_computed() -> None:
    queued: list[ResearchJob] = []

    for adapter, backend in (
        (DistributedCPUAdapter(queued.append), ComputeBackend.DISTRIBUTED_CPU),
        (DistributedGPUAdapter(queued.append), ComputeBackend.DISTRIBUTED_GPU),
        (CloudHPCAdapter(queued.append), ComputeBackend.CLOUD_HPC),
    ):
        submission = adapter.submit(job(backend))
        assert submission.job_id == queued[-1].job_id
        assert submission.backend is backend
        assert queued[-1].status.value == "RAW"

    assert len(queued) == 3


def test_scheduler_adapter_rejects_backend_mismatch() -> None:
    adapter = DistributedCPUAdapter(lambda _: None)

    try:
        adapter.submit(job(ComputeBackend.DISTRIBUTED_GPU))
    except ValueError as exc:
        assert "backend" in str(exc)
    else:
        raise AssertionError("backend mismatch must fail closed")
