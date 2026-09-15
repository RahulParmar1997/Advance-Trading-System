from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID, uuid4

from advance_system.research.compute import ComputeBackend, ResearchJob


@dataclass(frozen=True, slots=True)
class ResearchSubmission:
    submission_id: UUID
    job_id: UUID
    backend: ComputeBackend


class SchedulerEnqueuer(Protocol):
    def __call__(self, job: ResearchJob) -> None:
        """Enqueue research work only; implementations must have no broker authority."""


class RemoteResearchAdapter:
    """Vendor-neutral scheduler adapter; it records handoff without claiming execution."""

    def __init__(self, backend: ComputeBackend, enqueue: SchedulerEnqueuer) -> None:
        if backend not in {
            ComputeBackend.DISTRIBUTED_CPU,
            ComputeBackend.DISTRIBUTED_GPU,
            ComputeBackend.CLOUD_HPC,
        }:
            raise ValueError("RemoteResearchAdapter requires a remote compute backend")
        self._backend = backend
        self._enqueue = enqueue

    def submit(self, job: ResearchJob) -> ResearchSubmission:
        job.validate()
        if job.backend is not self._backend:
            raise ValueError("research job backend does not match scheduler adapter")
        self._enqueue(job)
        return ResearchSubmission(uuid4(), job.job_id, self._backend)


class DistributedCPUAdapter(RemoteResearchAdapter):
    def __init__(self, enqueue: SchedulerEnqueuer) -> None:
        super().__init__(ComputeBackend.DISTRIBUTED_CPU, enqueue)


class DistributedGPUAdapter(RemoteResearchAdapter):
    def __init__(self, enqueue: SchedulerEnqueuer) -> None:
        super().__init__(ComputeBackend.DISTRIBUTED_GPU, enqueue)


class CloudHPCAdapter(RemoteResearchAdapter):
    def __init__(self, enqueue: SchedulerEnqueuer) -> None:
        super().__init__(ComputeBackend.CLOUD_HPC, enqueue)
