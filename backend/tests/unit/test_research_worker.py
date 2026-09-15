import asyncio

import pytest

from advance_system.research.compute import ResearchJob, ResourceLimits
from advance_system.research.worker import ResearchExecutionTimeout, ResearchWorkerRunner


def job(*, max_seconds: int = 1) -> ResearchJob:
    return ResearchJob.create(
        dataset_version="dataset-v1",
        strategy_version="strategy-v1",
        feature_version="features-v1",
        configuration_version="config-v1",
        git_commit_sha="a" * 40,
        random_seed=7,
        resource_limits=ResourceLimits(max_seconds=max_seconds),
    )


@pytest.mark.asyncio
async def test_worker_completes_within_wall_clock_limit() -> None:
    async def worker(research_job: ResearchJob) -> bytes:
        assert research_job.job_id is not None
        await asyncio.sleep(0)
        return b"result"

    research_job = job(max_seconds=1)
    runner = ResearchWorkerRunner()

    assert await runner.run(research_job, worker) == b"result"
    assert not runner.is_running(research_job.job_id)


@pytest.mark.asyncio
async def test_worker_timeout_cancels_underlying_task() -> None:
    cancelled = asyncio.Event()

    async def worker(research_job: ResearchJob) -> bytes:
        try:
            await asyncio.sleep(60)
        finally:
            cancelled.set()
        return b"unreachable"

    research_job = job(max_seconds=1)
    runner = ResearchWorkerRunner()

    with pytest.raises(ResearchExecutionTimeout, match="max_seconds=1"):
        await runner.run(research_job, worker)

    assert cancelled.is_set()
    assert not runner.is_running(research_job.job_id)


@pytest.mark.asyncio
async def test_explicit_cancel_stops_running_worker() -> None:
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def worker(research_job: ResearchJob) -> bytes:
        started.set()
        try:
            await asyncio.sleep(60)
        finally:
            cancelled.set()
        return b"unreachable"

    research_job = job(max_seconds=60)
    runner = ResearchWorkerRunner()
    execution = asyncio.create_task(runner.run(research_job, worker))
    await started.wait()

    assert await runner.cancel(research_job.job_id)
    with pytest.raises(asyncio.CancelledError):
        await execution
    assert cancelled.is_set()
    assert not runner.is_running(research_job.job_id)


@pytest.mark.asyncio
async def test_cancel_unknown_job_is_noop() -> None:
    runner = ResearchWorkerRunner()
    assert not await runner.cancel(job().job_id)
