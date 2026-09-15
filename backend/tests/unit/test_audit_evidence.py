from datetime import datetime, timezone

import pytest

from advance_system.audit import AuditDecisionKind, AuditEvidenceRecord, InMemoryAuditEvidenceStore


OBSERVED_AT = datetime(2026, 9, 15, 9, 30, tzinfo=timezone.utc)


def make_record(kind: AuditDecisionKind = AuditDecisionKind.SCANNER) -> AuditEvidenceRecord:
    return AuditEvidenceRecord(
        decision_kind=kind,
        decision_id="decision-1",
        observed_at=OBSERVED_AT,
        instrument="NSE_EQ|INE001",
        timeframe_seconds=300,
        explanation="scanner matched the configured evidence",
        evidence=(
            {"field": "trend", "operator": "eq", "expected": "UP", "observed": "UP", "matched": True},
        ),
    )


def test_record_is_immutable_and_explicitly_not_execution_authority() -> None:
    record = make_record().finalized()
    assert record.execution_authority is False
    assert record.record_id == record.compute_record_id()
    with pytest.raises(AttributeError):
        record.explanation = "changed"  # type: ignore[misc]


def test_store_is_append_only_and_idempotent() -> None:
    store = InMemoryAuditEvidenceStore()
    record = make_record()
    record_id = store.append(record)
    assert store.append(record) == record_id
    assert len(store.all()) == 1
    assert store.get(record_id) == store.all()[0]


def test_record_id_is_content_addressed_and_changes_with_evidence() -> None:
    first = make_record().finalized()
    second = AuditEvidenceRecord(
        decision_kind=first.decision_kind,
        decision_id=first.decision_id,
        observed_at=first.observed_at,
        instrument=first.instrument,
        timeframe_seconds=first.timeframe_seconds,
        explanation=first.explanation,
        evidence=({"field": "trend", "operator": "eq", "expected": "DOWN", "observed": "UP", "matched": False},),
    ).finalized()
    assert first.record_id != second.record_id


def test_all_decision_kinds_are_supported() -> None:
    store = InMemoryAuditEvidenceStore()
    for kind in AuditDecisionKind:
        store.append(make_record(kind))
    assert {record.decision_kind for record in store.all()} == set(AuditDecisionKind)


def test_execution_authority_cannot_be_enabled() -> None:
    with pytest.raises(ValueError, match="execution authority"):
        AuditEvidenceRecord(
            decision_kind=AuditDecisionKind.RISK,
            decision_id="risk-1",
            observed_at=OBSERVED_AT,
            explanation="risk decision recorded",
            execution_authority=True,
        ).validate()


def test_future_or_naive_timestamps_fail_closed() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_record(). __class__(
            decision_kind=AuditDecisionKind.SCANNER,
            decision_id="decision-2",
            observed_at=datetime(2026, 9, 15, 9, 30),
            explanation="x",
        ).validate()
    with pytest.raises(ValueError, match="future"):
        AuditEvidenceRecord(
            decision_kind=AuditDecisionKind.SCANNER,
            decision_id="decision-3",
            observed_at=datetime.now(timezone.utc).replace(year=2099),
            explanation="x",
        ).validate()
