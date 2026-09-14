from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Iterable

from advance_system.domain.market_events import QuoteEvent
from advance_system.market.session import IndiaMarketSession, SessionPhase


@dataclass(frozen=True, slots=True)
class Candle:
    instrument: str
    start: datetime
    end: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    session_date: date | None = None
    session_phase: SessionPhase | None = None


class CandleEngine:
    """Build fixed-time candles without crossing India trading sessions."""

    def __init__(self, interval_seconds: int = 60, session: IndiaMarketSession | None = None) -> None:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        self.interval_seconds = interval_seconds
        self.session = session
        self._current: dict[str, Candle] = {}
        self._last_timestamp: dict[str, datetime] = {}
        self._last_cumulative_volume: dict[str, int] = {}

    def update(self, event: QuoteEvent) -> Candle | None:
        event.validate()
        previous_timestamp = self._last_timestamp.get(event.instrument)
        if previous_timestamp is not None and event.timestamp < previous_timestamp:
            raise ValueError("out-of-order quote event")
        self._last_timestamp[event.instrument] = event.timestamp

        session_status = self.session.status_at(event.timestamp) if self.session else None
        if session_status is not None and session_status.phase is not SessionPhase.OPEN:
            raise ValueError(f"quote is outside regular trading session: {session_status.phase.value}")

        epoch = int(event.timestamp.timestamp())
        start_epoch = epoch - (epoch % self.interval_seconds)
        start = datetime.fromtimestamp(start_epoch, tz=event.timestamp.tzinfo)
        end = datetime.fromtimestamp(start_epoch + self.interval_seconds, tz=event.timestamp.tzinfo)
        current = self._current.get(event.instrument)

        if current is None:
            self._current[event.instrument] = self._new_candle(event, start, end, self._volume_delta(event), session_status)
            return None

        crosses_session = session_status is not None and current.session_date != session_status.session_date
        if start >= current.end or crosses_session:
            completed = current
            self._current[event.instrument] = self._new_candle(event, start, end, self._volume_delta(event), session_status)
            return completed

        delta = self._volume_delta(event)
        self._current[event.instrument] = Candle(
            current.instrument,
            current.start,
            current.end,
            current.open,
            max(current.high, event.last_price),
            min(current.low, event.last_price),
            event.last_price,
            current.volume + delta,
            current.session_date,
            current.session_phase,
        )
        return None

    def current_candles(self) -> tuple[Candle, ...]:
        return tuple(self._current.values())

    def _new_candle(self, event: QuoteEvent, start: datetime, end: datetime, volume: int, status) -> Candle:
        return Candle(
            event.instrument,
            start,
            end,
            event.last_price,
            event.last_price,
            event.last_price,
            event.last_price,
            volume,
            status.session_date if status else None,
            status.phase if status else None,
        )

    def _volume_delta(self, event: QuoteEvent) -> int:
        if event.volume is None:
            return 0
        previous = self._last_cumulative_volume.get(event.instrument)
        self._last_cumulative_volume[event.instrument] = event.volume
        if previous is None:
            return 0
        if event.volume < previous:
            raise ValueError("cumulative volume moved backwards")
        return event.volume - previous


class MultiTimeframeCandleEngine:
    """Maintain independent fixed-time candle streams for multiple intervals."""

    def __init__(self, intervals_seconds: Iterable[int], session: IndiaMarketSession | None = None) -> None:
        intervals = tuple(dict.fromkeys(intervals_seconds))
        if not intervals:
            raise ValueError("at least one candle interval is required")
        if any(interval <= 0 for interval in intervals):
            raise ValueError("candle intervals must be positive")
        self.intervals_seconds = intervals
        self._engines = {interval: CandleEngine(interval, session) for interval in intervals}

    def update(self, event: QuoteEvent) -> dict[int, Candle]:
        completed: dict[int, Candle] = {}
        for interval, engine in self._engines.items():
            candle = engine.update(event)
            if candle is not None:
                completed[interval] = candle
        return completed

    def current_candles(self) -> dict[int, tuple[Candle, ...]]:
        return {interval: engine.current_candles() for interval, engine in self._engines.items()}
