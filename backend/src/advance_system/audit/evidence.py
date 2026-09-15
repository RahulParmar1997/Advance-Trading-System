from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json
from threading import RLock
from typing import Mapping, Protocol


class AuditDecisionKind(StrEnum):
    SCANNER = "SCANNER"
    SCORE = "SCORE"
    PROBABILITY = "PROBABILITY"
    RISK = "RISK"


@dataclass(frozen=True, slots=True)
class AuditEvidenceRecord:
    """Immutable explanation/provenance record; never an execution authority."""

    decision_kind: AuditDecisionKind
    decision_id: str
    observed_at: datetime
    explanation: str
    evidence: tuple[Mapping[str, object], ...] = ()
    instrument: str | None = None
    timeframe_seconds: int | None = None
    contract_version: int = 1
    execution_authority: bool = False
    record_id: str = ""

    def validate(self) -> None:
        if not isinstance(self.decision_kind, AuditDecisionKind):
            raise ValueError("decision_kind must be an AuditDecisionKind")
        if not self.decision_id.strip():
            raise ValueError("decision_id is required")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.observed_at > datetime.now(timezone.utc):
            raise ValueError("observed_at cannot be in the future")
        if not self.explanation.strip():
            raise ValueError("explanation is required")
        if self.instrument is not None and not self.instrument.strip():
            raise ValueError("instrument cannot be empty")
        if self.timeframe_seconds is not None and self.timeframe_seconds <= 0:
            raise ValueError("timeframe_seconds must be positive")
        if self.contract_version <= 0:
            raise ValueError("contract_version must be positive")
        if self.execution_authority:
            raise ValueError("audit evidence cannot have execution authority")
        for item in self.evidence:
            if not isinstance(item, Mapping):
                raise ValueError("evidence entries must be mappings")
        if self.record_id and self.record_id != self.compute_record_id():
            raise ValueError("record_id does not match immutable record content")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "decision_kind": self.decision_kind.value,
            "decision_id": self.decision_id,
            "observed_at": self.observed_at.astimezone(timezone.utc).isoformat(),
            "explanation": self.explanation,
            "evidence": [dict(item) for item in self.evidence],
            "instrument": self.instrument,
            "timeframe_seconds": self.timeframe_seconds,
            "contract_version": self.contract_version,
            "execution_authority": False,
        }

    def compute_record_id(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(), sort_keys=True, separators=(",", ":"), default=str
        ).encode("utf-8")
        return sha256(encoded).hexdigest()

    def finalized(self) -> "AuditEvidenceRecord":
        self.validate()
        return AuditEvidenceRecord(
            decision_kind=self.decision_kind,
            decision_id=self.decision_id,
            observed_at=self.observed_at,
            explanation=self.explanation,
            evidence=self.evidence,
            instrument=self.instrument,
            timeframe_seconds=self.timeframe_seconds,
            contract_version=self.contract_version,
            execution_authority=False,
            record_id=self.compute_record_id(),
        )


class AuditEvidenceStore(Protocol):
    """Append-only persistence boundary for audit evidence."""

    def append(self, record: AuditEvidenceRecord) -> str:
        """Persist an audit record and return its immutable record id."""

    def get(self, record_id: str) -> AuditEvidenceRecord | None:
        """Read audit evidence; this API exposes no execution capability."""

    def all(self) -> tuple[AuditEvidenceRecord, ...]:
        """Return records in append order."""


class InMemoryAuditEvidenceStore:
    """Reference append-only store; replaceable by a durable backend later."""

    def __init__(self) -> None:
        self._records: dict[str, AuditEvidenceRecord] = {}
        self._order: list[str] = []
        self._lock = RLock()

    def append(self, record: AuditEvidenceRecord) -> str:
        finalized = record.finalized()
        with self._lock:
            existing = self._records.get(finalized.record_id)
            if existing is not None:
                return finalized.record_id
            self._records[finalized.record_id] = finalized
            self._order.append(finalized.record_id)
            return finalized.record_id

    def get(self, record_id: str) -> AuditEvidenceRecord | None:
        with self._lock:
            return self._records.get(record_id)

    def all(self) -> tuple[AuditEvidenceRecord, ...]:
        with self._lock:
            return tuple(self._records[record_id] for record_id in self._order)
