from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from advance_system.domain.market_events import QuoteEvent


@dataclass(frozen=True, slots=True)
class QualityObservation:
    instrument: str
    timestamp: datetime
    accepted: bool
    code: str
    reason: str


class DataQualityService:
    """Tracks quote freshness, ordering, duplicates and timestamp gaps."""

    def __init__(self, *, max_age: timedelta = timedelta(seconds=10), max_gap: timedelta = timedelta(seconds=30)) -> None:
        if max_age <= timedelta(0) or max_gap <= timedelta(0):
            raise ValueError("quality thresholds must be positive")
        self.max_age = max_age
        self.max_gap = max_gap
        self._last_timestamp: dict[str, datetime] = {}
        self._seen: set[tuple[str, datetime]] = set()

    def observe(self, event: QuoteEvent, *, now: datetime) -> QualityObservation:
        try:
            event.validate()
        except ValueError as exc:
            return QualityObservation(event.instrument, event.timestamp, False, "INVALID", str(exc))
        if now.tzinfo is None or event.timestamp.tzinfo is None:
            return QualityObservation(event.instrument, event.timestamp, False, "INVALID", "timestamps must be timezone-aware")
        if event.timestamp > now:
            return QualityObservation(event.instrument, event.timestamp, False, "FUTURE", "event timestamp is in the future")
        if now - event.timestamp > self.max_age:
            return QualityObservation(event.instrument, event.timestamp, False, "STALE", "quote is stale")
        key = (event.instrument, event.timestamp)
        if key in self._seen:
            return QualityObservation(event.instrument, event.timestamp, False, "DUPLICATE", "duplicate timestamp for instrument")
        previous = self._last_timestamp.get(event.instrument)
        if previous is not None and event.timestamp < previous:
            return QualityObservation(event.instrument, event.timestamp, False, "OUT_OF_ORDER", "timestamp is older than latest accepted event")
        if previous is not None and event.timestamp - previous > self.max_gap:
            self._seen.add(key)
            self._last_timestamp[event.instrument] = event.timestamp
            return QualityObservation(event.instrument, event.timestamp, True, "GAP", "quote accepted after a timestamp gap")
        self._seen.add(key)
        self._last_timestamp[event.instrument] = event.timestamp
        return QualityObservation(event.instrument, event.timestamp, True, "VALID", "quote accepted")
