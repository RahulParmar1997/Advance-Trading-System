from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol
from uuid import UUID, uuid4


class ComputeBackend(StrEnum):
    LOCAL_CPU = "LOCAL_CPU"
    LOCAL_GPU = "LOCAL_GPU"
    DISTRIBUTED_CPU = "DISTRIBUTED_CPU"
    DISTRIBUTED_GPU = "DISTRIBUTED_GPU"
    CLOUD_HPC = "CLOUD_HPC"


class ResearchStatus(StrEnum):
    RAW = "RAW"
    COMPUTED = "COMPUTED"
    VALIDATED = "VALIDATED"
    OOS_VALIDATED = "OOS_VALIDATED"
    RESEARCH_APPROVED = "RESEARCH_APPROVED"


@dataclass(frozen=True, slots=True)
class ResourceLimits:
    max_seconds: int = 3600
    max_concurrency: int = 1
    max_storage_bytes: int = 10_000_000_000

    def validate(self) -> None:
        if self.max_seconds <= 0:
            raise ValueError("max_seconds must be positive")
        if self.max_concurrency <= 0:
            raise ValueError("max_concurrency must be positive")
        if self.max_storage_bytes <= 0:
            raise ValueError("max_storage_bytes must be positive")


@dataclass(frozen=True, slots=True)
class ResearchJob:
    job_id: UUID
    dataset_version: str
    strategy_version: str
    feature_version: str
    configuration_version: str
    git_commit_sha: str
    random_seed: int
    backend: ComputeBackend
    status: ResearchStatus = ResearchStatus.RAW
    resource_limits: ResourceLimits = ResourceLimits()

    def validate(self) -> None:
        for name, value in (
            ("dataset_version", self.dataset_version),
            ("strategy_version", self.strategy_version),
            ("feature_version", self.feature_version),
            ("configuration_version", self.configuration_version),
            ("git_commit_sha", self.git_commit_sha),
        ):
            if not value:
                raise ValueError(f"{name} is required")
        if self.random_seed < 0:
            raise ValueError("random_seed must be non-negative")
        self.resource_limits.validate()

    @classmethod
    def create(
        cls,
        *,
        dataset_version: str,
        strategy_version: str,
        feature_version: str,
        configuration_version: str,
        git_commit_sha: str,
        random_seed: int,
        backend: ComputeBackend = ComputeBackend.LOCAL_CPU,
        resource_limits: ResourceLimits | None = None,
    ) -> ResearchJob:
        job = cls(
            job_id=uuid4(),
            dataset_version=dataset_version,
            strategy_version=strategy_version,
            feature_version=feature_version,
            configuration_version=configuration_version,
            git_commit_sha=git_commit_sha,
            random_seed=random_seed,
            backend=backend,
            resource_limits=resource_limits or ResourceLimits(),
        )
        job.validate()
        return job


class ResearchExecutor(Protocol):
    def submit(self, job: ResearchJob) -> ResearchJob:
        """Submit research only; implementations must have no execution authority."""


class LocalResearchExecutor:
    """Safe deterministic scheduler boundary; it never submits broker orders."""

    def submit(self, job: ResearchJob) -> ResearchJob:
        job.validate()
        if job.backend not in {ComputeBackend.LOCAL_CPU, ComputeBackend.LOCAL_GPU}:
            raise ValueError("LocalResearchExecutor accepts only local compute backends")
        return ResearchJob(
            job_id=job.job_id,
            dataset_version=job.dataset_version,
            strategy_version=job.strategy_version,
            feature_version=job.feature_version,
            configuration_version=job.configuration_version,
            git_commit_sha=job.git_commit_sha,
            random_seed=job.random_seed,
            backend=job.backend,
            status=ResearchStatus.COMPUTED,
            resource_limits=job.resource_limits,
        )
