from datetime import datetime, timezone

import pytest

from advance_system.journal.audit import AuditEvent
from advance_system.journal.durable import JsonlAuditJournal


def event(event_id: str = "e1") -> AuditEvent:
    return AuditEvent(
        event_id=event_id,
        timestamp=datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc),
        event_type="POSITION_UPDATED",
        entity_id="NSE_EQ|TEST",
        payload={"quantity": "10"},
    )


def test_journal_round_trips_events(tmp_path):
    path = tmp_path / "journal.jsonl"
    journal = JsonlAuditJournal(path)
    journal.append(event())

    restored = JsonlAuditJournal(path)
    assert restored.events() == (event(),)
    assert restored.checkpoint().last_event_id == "e1"


def test_journal_rejects_duplicate_event_id(tmp_path):
    journal = JsonlAuditJournal(tmp_path / "journal.jsonl")
    journal.append(event())
    with pytest.raises(ValueError, match="duplicate event_id"):
        journal.append(event())


def test_journal_fails_closed_on_corrupt_record(tmp_path):
    path = tmp_path / "journal.jsonl"
    path.write_text('{"event_id":"bad"}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="invalid journal record"):
        JsonlAuditJournal(path)


def test_journal_checkpoint_is_empty_initially(tmp_path):
    checkpoint = JsonlAuditJournal(tmp_path / "journal.jsonl").checkpoint()
    assert checkpoint.event_count == 0
    assert checkpoint.last_event_id is None
