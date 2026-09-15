from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import RLock

from advance_system.journal.audit import AuditEvent


@dataclass(frozen=True, slots=True)
class JournalCheckpoint:
    event_count: int
    last_event_id: str | None


class JsonlAuditJournal:
    """Durable append-only JSONL journal boundary for PAPER/local operation."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._lock = RLock()
        self._events: list[AuditEvent] = []
        self._ids: set[str] = set()
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    raw = json.loads(line)
                    event = AuditEvent(
                        event_id=str(raw["event_id"]),
                        timestamp=datetime.fromisoformat(str(raw["timestamp"])),
                        event_type=str(raw["event_type"]),
                        entity_id=str(raw["entity_id"]),
                        payload={str(k): str(v) for k, v in dict(raw["payload"]).items()},
                    )
                    event.validate()
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    raise ValueError(f"invalid journal record at line {line_number}") from exc
                if event.event_id in self._ids:
                    raise ValueError(f"duplicate event_id at line {line_number}")
                self._events.append(event)
                self._ids.add(event.event_id)

    def append(self, event: AuditEvent) -> None:
        event.validate()
        with self._lock:
            if event.event_id in self._ids:
                raise ValueError("duplicate event_id")
            self._path.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "event_id": event.event_id,
                "timestamp": event.timestamp.astimezone(timezone.utc).isoformat(),
                "event_type": event.event_type,
                "entity_id": event.entity_id,
                "payload": dict(event.payload),
            }
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
                handle.flush()
            self._events.append(event)
            self._ids.add(event.event_id)

    def events(self) -> tuple[AuditEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def checkpoint(self) -> JournalCheckpoint:
        with self._lock:
            return JournalCheckpoint(len(self._events), self._events[-1].event_id if self._events else None)
