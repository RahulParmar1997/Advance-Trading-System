from datetime import datetime, timedelta, timezone

import pytest

from advance_system.observability.providers import (
    TerminalSnapshot,
    ValidatedTerminalSnapshotStore,
)


def test_store_publishes_and_returns_fresh_authoritative_snapshot() -> None:
    store = ValidatedTerminalSnapshotStore(max_age=timedelta(seconds=30))
    snapshot = TerminalSnapshot(view="market-state", data={"source": "upstream"})

    store.publish(snapshot, observed_at=datetime.now(timezone.utc))

    assert store.snapshot("market-state") == snapshot


def test_store_withholds_expired_snapshot() -> None:
    store = ValidatedTerminalSnapshotStore(max_age=timedelta(seconds=30))
    snapshot = TerminalSnapshot(view="risk", data={"source": "upstream"})

    store.publish(
        snapshot,
        observed_at=datetime.now(timezone.utc) - timedelta(seconds=31),
    )

    assert store.snapshot("risk") is None


def test_store_rejects_naive_observation_timestamp() -> None:
    store = ValidatedTerminalSnapshotStore(max_age=timedelta(seconds=30))

    with pytest.raises(ValueError, match="timezone-aware"):
        store.publish(
            TerminalSnapshot(view="portfolio", data={}),
            observed_at=datetime.now(),
        )


def test_store_rejects_future_observation_timestamp() -> None:
    store = ValidatedTerminalSnapshotStore(max_age=timedelta(seconds=30))

    with pytest.raises(ValueError, match="cannot be in the future"):
        store.publish(
            TerminalSnapshot(view="scanner", data={}),
            observed_at=datetime.now(timezone.utc) + timedelta(seconds=1),
        )


def test_store_rejects_non_positive_max_age() -> None:
    with pytest.raises(ValueError, match="max_age must be positive"):
        ValidatedTerminalSnapshotStore(max_age=timedelta(0))
