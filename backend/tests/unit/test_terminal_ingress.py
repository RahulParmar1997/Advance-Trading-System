from datetime import datetime, timedelta, timezone

import pytest

from advance_system.observability.ingress import (
    AuthoritativeTerminalObservation,
    TerminalSnapshotIngress,
)
from advance_system.observability.providers import (
    TerminalSnapshot,
    ValidatedTerminalSnapshotStore,
)


class AcceptingValidator:
    def validate(self, observation: AuthoritativeTerminalObservation) -> None:
        if not observation.snapshot.data:
            raise ValueError("empty authoritative observation")


class RejectingValidator:
    def validate(self, observation: AuthoritativeTerminalObservation) -> None:
        raise ValueError("observation rejected")


def test_ingress_publishes_only_after_validation() -> None:
    store = ValidatedTerminalSnapshotStore(max_age=timedelta(seconds=30))
    ingress = TerminalSnapshotIngress(store, AcceptingValidator())
    snapshot = TerminalSnapshot(view="market-state", data={"source": "upstream"})
    observed_at = datetime.now(timezone.utc)

    ingress.publish(AuthoritativeTerminalObservation(snapshot, observed_at))

    assert store.snapshot("market-state") == snapshot


def test_ingress_does_not_publish_rejected_observation() -> None:
    store = ValidatedTerminalSnapshotStore(max_age=timedelta(seconds=30))
    ingress = TerminalSnapshotIngress(store, RejectingValidator())
    observation = AuthoritativeTerminalObservation(
        TerminalSnapshot(view="risk", data={"source": "upstream"}),
        datetime.now(timezone.utc),
    )

    with pytest.raises(ValueError, match="observation rejected"):
        ingress.publish(observation)

    assert store.snapshot("risk") is None


def test_ingress_convenience_method_uses_same_validation_boundary() -> None:
    store = ValidatedTerminalSnapshotStore(max_age=timedelta(seconds=30))
    ingress = TerminalSnapshotIngress(store, AcceptingValidator())
    observed_at = datetime.now(timezone.utc)

    ingress.publish_view("portfolio", {"source": "upstream"}, observed_at=observed_at)

    assert store.snapshot("portfolio") == TerminalSnapshot(
        view="portfolio",
        data={"source": "upstream"},
    )
