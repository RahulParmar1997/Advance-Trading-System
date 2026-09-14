from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: str
    timestamp: datetime
    event_type: str
    entity_id: str
    payload: Mapping[str, str]

    def validate(self) -> None:
        if not self.event_id or not self.entity_id or not self.event_type:
            raise ValueError("event identity fields are required")
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")


class InMemoryAuditJournal:
    """Append-only journal boundary for PAPER/testing; persistence comes later."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
        self._ids: set[str] = set()

    def append(self, event: AuditEvent) -> None:
        event.validate()
        if event.event_id in self._ids:
            raise ValueError("duplicate event_id")
        self._events.append(event)
        self._ids.add(event.event_id)

    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)
