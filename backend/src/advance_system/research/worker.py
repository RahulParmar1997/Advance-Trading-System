from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Protocol
from uuid import UUID

from advance_system.research.compute import ResearchJob


class ResearchWorker(Protocol):
    def __call__(self, job: ResearchJob) -> Awaitable[bytes]:
        """Execute research work only; implementations have no broker authority."""


class ResearchExecutionTimeout(TimeoutError):
    """Research execution exceeded the job's configured wall-clock limit."""


class ResearchWorkerRunner:
    """Run research workers with fail-closed timeout and cancellation enforcement."""

    def __init__(self) -> None:
        self._tasks: dict[UUID, asyncio.Task[bytes]] = {}

    async def run(self, job: ResearchJob, worker: ResearchWorker) -> bytes:
        job.validate()
        if job.job_id in self._tasks:
            raise ValueError("research job is already running")

        task = asyncio.create_task(worker(job))
        self._tasks[job.job_id] = task
        try:
            try:
                return await asyncio.wait_for(task, timeout=job.resource_limits.max_seconds)
            except TimeoutError as exc:
                raise ResearchExecutionTimeout(
                    f"research job exceeded max_seconds={job.resource_limits.max_seconds}"
                ) from exc
        finally:
            self._tasks.pop(job.job_id, None)

    async def cancel(self, job_id: UUID) -> bool:
        task = self._tasks.get(job_id)
        if task is None:
            return False
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        return True

    def is_running(self, job_id: UUID) -> bool:
        task = self._tasks.get(job_id)
        return task is not None and not task.done()
