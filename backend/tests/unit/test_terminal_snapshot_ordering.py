from datetime import datetime, timedelta, timezone

import pytest

from advance_system.observability.providers import (
    TerminalSnapshot,
    ValidatedTerminalSnapshotStore,
)


def test_older_observation_cannot_replace_newer_snapshot() -> None:
    store = ValidatedTerminalSnapshotStore(max_age=timedelta(minutes=5))
    newer = datetime.now(timezone.utc) - timedelta(seconds=2)
    older = newer - timedelta(seconds=1)
    store.publish(TerminalSnapshot("market-state", {"price": 101}), observed_at=newer)

    with pytest.raises(ValueError, match="older than stored"):
        store.publish(TerminalSnapshot("market-state", {"price": 100}), observed_at=older)

    assert store.snapshot("market-state") == TerminalSnapshot("market-state", {"price": 101})


def test_identical_observation_is_idempotent() -> None:
    store = ValidatedTerminalSnapshotStore(max_age=timedelta(minutes=5))
    observed_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    snapshot = TerminalSnapshot("scanner", {"symbols": ["NIFTY"]})

    store.publish(snapshot, observed_at=observed_at)
    store.publish(snapshot, observed_at=observed_at)

    assert store.snapshot("scanner") == snapshot


def test_conflicting_observation_at_same_timestamp_is_rejected() -> None:
    store = ValidatedTerminalSnapshotStore(max_age=timedelta(minutes=5))
    observed_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    store.publish(TerminalSnapshot("risk", {"status": "ok"}), observed_at=observed_at)

    with pytest.raises(ValueError, match="conflicting snapshot"):
        store.publish(TerminalSnapshot("risk", {"status": "blocked"}), observed_at=observed_at)
