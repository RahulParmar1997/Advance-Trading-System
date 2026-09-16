from __future__ import annotations

from dataclasses import dataclass
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
