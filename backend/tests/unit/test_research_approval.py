from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from advance_system.research.approval import ResearchApprovalWorkflow
from advance_system.research.calibration import CalibrationValidation
from advance_system.research.compute import ComputeBackend, ResearchStatus
from advance_system.research.results import (
    EnvironmentMetadata,
    HardwareMetadata,
    ResearchResultManifest,
    ResourceUsage,
)

NOW = datetime(2026, 9, 15, 12, 0, tzinfo=UTC)


def manifest() -> ResearchResultManifest:
    from advance_system.research.compute import ResearchJob

    job = ResearchJob(
        job_id=uuid4(),
        dataset_version="dataset-v1",
        strategy_version="strategy-v1",
        feature_version="features-v1",
        configuration_version="config-v1",
        git_commit_sha="a" * 40,
        random_seed=7,
        backend=ComputeBackend.LOCAL_CPU,
        status=ResearchStatus.COMPUTED,
    )
    return ResearchResultManifest.from_job(
        job,
        b"result",
        hardware=HardwareMetadata(cpu="actual-cpu"),
        environment=EnvironmentMetadata(os="Linux", python="3.11", runtime="pytest"),
        resource_usage=ResourceUsage(elapsed_seconds=1, storage_bytes=6, concurrency=1),
        created_at=NOW,
    )


def validation() -> CalibrationValidation:
    return CalibrationValidation(
        observations=10,
        brier_score=Decimal("0.1"),
        log_loss=Decimal("0.2"),
        accuracy=Decimal("0.8"),
    )


def test_computed_result_enters_oos_validated_state() -> None:
    record = ResearchApprovalWorkflow().validate_oos(manifest(), validation())

    assert record.status is ResearchStatus.OOS_VALIDATED
    assert record.approved_at is None


def test_only_oos_validated_result_can_be_approved() -> None:
    workflow = ResearchApprovalWorkflow()
    record = workflow.validate_oos(manifest(), validation())

    approved = workflow.approve(record, approved_at=NOW)

    assert approved.status is ResearchStatus.RESEARCH_APPROVED
    assert approved.approved_at == NOW


def test_approval_is_bound_to_result_provenance() -> None:
    workflow = ResearchApprovalWorkflow()
    first = manifest()
    record = workflow.validate_oos(first, validation())
    second = manifest()

    with pytest.raises(ValueError, match="not bound"):
        workflow.verify_binding(second, record)


def test_approval_cannot_bypass_oos_validation() -> None:
    workflow = ResearchApprovalWorkflow()
    record = workflow.validate_oos(manifest(), validation())
    approved = workflow.approve(record, approved_at=NOW)

    with pytest.raises(ValueError, match="only OOS_VALIDATED"):
        workflow.approve(approved, approved_at=NOW)


def test_approval_requires_timezone_aware_timestamp() -> None:
    workflow = ResearchApprovalWorkflow()
    record = workflow.validate_oos(manifest(), validation())

    with pytest.raises(ValueError, match="timezone-aware"):
        workflow.approve(record, approved_at=datetime(2026, 9, 15, 12, 0))
