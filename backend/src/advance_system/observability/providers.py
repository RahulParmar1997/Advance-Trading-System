from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Protocol

from advance_system.observability.api import TerminalViewResponse, ViewName, unavailable_view


@dataclass(frozen=True, slots=True)
class TerminalSnapshot:
    """Provider-owned observational payload; values must originate outside the HTTP layer."""

    view: ViewName
    data: object


class TerminalSnapshotProvider(Protocol):
    """Read-only provider boundary for authoritative terminal observations."""

    def snapshot(self, view: ViewName) -> TerminalSnapshot | None:
        """Return a validated provider snapshot, or None when the provider has no data."""
        ...


class ValidatedTerminalSnapshotStore:
    """Thread-safe store for snapshots already validated by an authoritative source.

    Publishing requires an aware observation timestamp. The store never creates market
    or account values; expired observations are withheld so the terminal fails closed.
    """

    def __init__(self, *, max_age: timedelta) -> None:
        if max_age <= timedelta(0):
            raise ValueError("max_age must be positive")
        self._max_age = max_age
        self._snapshots: dict[ViewName, tuple[TerminalSnapshot, datetime]] = {}
        self._lock = Lock()

    def publish(self, snapshot: TerminalSnapshot, *, observed_at: datetime) -> None:
        if observed_at.tzinfo is None or observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        if not snapshot.view:
            raise ValueError("snapshot view is required")
        with self._lock:
            self._snapshots[snapshot.view] = (snapshot, observed_at.astimezone(timezone.utc))

    def snapshot(self, view: ViewName) -> TerminalSnapshot | None:
        with self._lock:
            entry = self._snapshots.get(view)
        if entry is None:
            return None
        snapshot, observed_at = entry
        if datetime.now(timezone.utc) - observed_at > self._max_age:
            return None
        return snapshot


class TerminalDataService:
    """Maps provider snapshots to the stable terminal API without synthesizing values."""

    def __init__(self, provider: TerminalSnapshotProvider | None = None) -> None:
        self.provider = provider

    def get(self, view: ViewName) -> TerminalViewResponse:
        if self.provider is None:
            return unavailable_view(view)
        snapshot = self.provider.snapshot(view)
        if snapshot is None or snapshot.view != view:
            return unavailable_view(view)
        return TerminalViewResponse(
            schema_version="v1",
            view=view,
            mode="PAPER",
            available=True,
            reason="provider_snapshot",
            data=snapshot.data,
        )
