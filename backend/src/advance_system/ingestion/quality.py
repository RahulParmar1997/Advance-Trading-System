from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from advance_system.domain.market_events import QuoteEvent


class DataQualityCode:
    VALID = "VALID"
    STALE = "STALE"
    OUT_OF_ORDER = "OUT_OF_ORDER"
    DUPLICATE = "DUPLICATE"
    INVALID = "INVALID"
    VOLUME_REGRESSION = "VOLUME_REGRESSION"


@dataclass(frozen=True, slots=True)
class DataQualityResult:
    accepted: bool
    code: str
    reason: str


class QuoteQualityGate:
    """Deterministic stateful quality gate for canonical quote events.

    The gate rejects malformed, stale, duplicate, out-of-order and
    cumulative-volume-regressing events. It keeps no broker-specific state.
    """

    def __init__(self, *, max_age: timedelta = timedelta(seconds=10)) -> None:
        if max_age <= timedelta(0):
            raise ValueError("max_age must be positive")
        self.max_age = max_age
        self._last_timestamp: dict[str, datetime] = {}
        self._last_event_key: set[tuple[str, datetime, Decimal]] = set()
        self._last_cumulative_volume: dict[str, int] = {}

    def evaluate(self, event: QuoteEvent, *, now: datetime) -> DataQualityResult:
        try:
            event.validate()
        except ValueError as exc:
            return DataQualityResult(False, DataQualityCode.INVALID, str(exc))

        if now.tzinfo is None or event.timestamp.tzinfo is None:
            return DataQualityResult(False, DataQualityCode.INVALID, "timestamps must be timezone-aware")
        if now < event.timestamp:
            return DataQualityResult(False, DataQualityCode.INVALID, "event timestamp is in the future")
        if now - event.timestamp > self.max_age:
            return DataQualityResult(False, DataQualityCode.STALE, "quote is stale")

        key = (event.instrument, event.timestamp, event.last_price)
        if key in self._last_event_key:
            return DataQualityResult(False, DataQualityCode.DUPLICATE, "duplicate quote event")

        previous = self._last_timestamp.get(event.instrument)
        if previous is not None and event.timestamp < previous:
            return DataQualityResult(False, DataQualityCode.OUT_OF_ORDER, "quote is older than the latest accepted quote")

        if event.volume is not None:
            previous_volume = self._last_cumulative_volume.get(event.instrument)
            if previous_volume is not None and event.volume < previous_volume:
                return DataQualityResult(False, DataQualityCode.VOLUME_REGRESSION, "cumulative volume regressed")

        self._last_timestamp[event.instrument] = event.timestamp
        self._last_event_key.add(key)
        if event.volume is not None:
            self._last_cumulative_volume[event.instrument] = event.volume
        return DataQualityResult(True, DataQualityCode.VALID, "quote accepted")
