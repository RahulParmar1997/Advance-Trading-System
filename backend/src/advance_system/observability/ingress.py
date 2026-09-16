from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from advance_system.observability.api import ViewName
from advance_system.observability.providers import TerminalSnapshot, ValidatedTerminalSnapshotStore


@dataclass(frozen=True, slots=True)
class AuthoritativeTerminalObservation:
    """An upstream observation presented for terminal publication."""

    snapshot: TerminalSnapshot
    observed_at: datetime


class TerminalObservationValidator(Protocol):
    """Upstream validation boundary; implementations own source-specific validation."""

    def validate(self, observation: AuthoritativeTerminalObservation) -> None:
        """Raise ValueError when the observation is not authoritative and valid."""
        ...


class TerminalSnapshotIngress:
    """Publish only observations explicitly accepted by an upstream validator."""

    def __init__(
        self,
        store: ValidatedTerminalSnapshotStore,
        validator: TerminalObservationValidator,
    ) -> None:
        self._store = store
        self._validator = validator

    def publish(self, observation: AuthoritativeTerminalObservation) -> None:
        self._validator.validate(observation)
        self._store.publish(
            observation.snapshot,
            observed_at=observation.observed_at,
        )

    def publish_view(
        self,
        view: ViewName,
        data: object,
        *,
        observed_at: datetime,
    ) -> None:
        """Convenience boundary; validation still occurs before persistence."""
        self.publish(
            AuthoritativeTerminalObservation(
                snapshot=TerminalSnapshot(view=view, data=data),
                observed_at=observed_at,
            )
        )
