from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

from advance_system.journal.audit import AuditEvent


class JsonlAuditJournal:
    """Durable append-only JSONL journal boundary; one event per line."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._lock = Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: AuditEvent) -> None:
        event.validate()
        record = {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "entity_id": event.entity_id,
            "payload": dict(event.payload),
        }
        with self._lock:
            if self._contains(event.event_id):
                raise ValueError("duplicate event_id")
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")

    def _contains(self, event_id: str) -> bool:
        if not self._path.exists():
            return False
        with self._path.open("r", encoding="utf-8") as handle:
            return any(json.loads(line).get("event_id") == event_id for line in handle if line.strip())
