from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from advance_system.research.calibration import CalibrationValidation
from advance_system.research.compute import ResearchStatus
from advance_system.research.results import ResearchResultManifest


@dataclass(frozen=True, slots=True)
class ResearchApprovalRecord:
    """Immutable OOS validation/approval evidence bound to one computed result."""

    job_id: UUID
    result_sha256: str
    validation: CalibrationValidation
    status: ResearchStatus
    approved_at: datetime | None = None

    def validate(self) -> None:
        if self.status not in {ResearchStatus.OOS_VALIDATED, ResearchStatus.RESEARCH_APPROVED}:
            raise ValueError("research approval record must be OOS_VALIDATED or RESEARCH_APPROVED")
        if len(self.result_sha256) != 64 or any(
            char not in "0123456789abcdef" for char in self.result_sha256
        ):
            raise ValueError("result_sha256 must be a lowercase SHA-256 hex digest")
        self.validation.validate()
        if self.status is ResearchStatus.RESEARCH_APPROVED:
            if self.approved_at is None or self.approved_at.tzinfo is None or self.approved_at.utcoffset() is None:
                raise ValueError("approved_at must be timezone-aware for approved research")
        elif self.approved_at is not None:
            raise ValueError("OOS_VALIDATED research must not have an approval timestamp")


class ResearchApprovalWorkflow:
    """Connect computed result provenance to OOS validation and explicit research approval."""

    def validate_oos(
        self,
        manifest: ResearchResultManifest,
        validation: CalibrationValidation,
    ) -> ResearchApprovalRecord:
        manifest.validate()
        if manifest.status is not ResearchStatus.COMPUTED:
            raise ValueError("only COMPUTED research results may enter OOS validation")
        validation.validate()
        record = ResearchApprovalRecord(
            job_id=manifest.job_id,
            result_sha256=manifest.result_sha256,
            validation=validation,
            status=ResearchStatus.OOS_VALIDATED,
        )
        record.validate()
        return record

    def approve(
        self,
        record: ResearchApprovalRecord,
        *,
        approved_at: datetime,
    ) -> ResearchApprovalRecord:
        record.validate()
        if record.status is not ResearchStatus.OOS_VALIDATED:
            raise ValueError("only OOS_VALIDATED research may be approved")
        if approved_at.tzinfo is None or approved_at.utcoffset() is None:
            raise ValueError("approved_at must be timezone-aware")
        approved = ResearchApprovalRecord(
            job_id=record.job_id,
            result_sha256=record.result_sha256,
            validation=record.validation,
            status=ResearchStatus.RESEARCH_APPROVED,
            approved_at=approved_at,
        )
        approved.validate()
        return approved

    @staticmethod
    def verify_binding(manifest: ResearchResultManifest, record: ResearchApprovalRecord) -> None:
        manifest.validate()
        record.validate()
        if record.job_id != manifest.job_id or record.result_sha256 != manifest.result_sha256:
            raise ValueError("research approval is not bound to the supplied result")
