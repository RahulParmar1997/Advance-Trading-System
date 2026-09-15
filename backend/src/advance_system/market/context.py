from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Sequence

from advance_system.market.candle_engine import Candle
from advance_system.market.regime import MarketRegime, MarketRegimeEngine, RegimeObservation
from advance_system.market.session import IndiaMarketSession, MarketSessionStatus
from advance_system.market.structure import SwingPoint


@dataclass(frozen=True, slots=True)
class MarketContextSnapshot:
    """Explicit session + regime state derived only from completed candle data."""

    instrument: str
    observed_at: datetime
    session: MarketSessionStatus
    regime: RegimeObservation

    @property
    def is_trade_session(self) -> bool:
        return self.session.is_open

    @property
    def regime_available(self) -> bool:
        return self.regime.regime is not MarketRegime.INSUFFICIENT_DATA

    @property
    def confidence(self) -> Decimal:
        return self.regime.confidence


class MarketContextEngine:
    """Join session metadata and deterministic regime classification safely.

    The engine accepts completed candles only. It rejects mixed instruments,
    timestamps, session dates, and future observations instead of guessing.
    """

    def __init__(
        self,
        session: IndiaMarketSession,
        regime_engine: MarketRegimeEngine | None = None,
    ) -> None:
        self.session = session
        self.regime_engine = regime_engine or MarketRegimeEngine()

    def build(
        self,
        candles: Sequence[Candle],
        swings: Sequence[SwingPoint] = (),
        *,
        observed_at: datetime | None = None,
    ) -> MarketContextSnapshot:
        if not candles:
            raise ValueError("completed candles cannot be empty")
        instrument = candles[0].instrument.strip()
        if not instrument:
            raise ValueError("candle instrument is required")
        if any(c.instrument.strip() != instrument for c in candles):
            raise ValueError("candles must contain one instrument")
        if any(c.end.tzinfo is None for c in candles):
            raise ValueError("candle timestamps must be timezone-aware")
        if any(c.end > candles[index + 1].end for index, c in enumerate(candles[:-1])):
            raise ValueError("candles must be chronological")

        context_time = observed_at or candles[-1].end
        if context_time.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if context_time < candles[-1].end:
            raise ValueError("observed_at cannot precede latest completed candle")

        status = self.session.status_at(context_time)
        regime = self.regime_engine.classify(candles, swings)

        candle_dates = {c.session_date for c in candles if c.session_date is not None}
        if len(candle_dates) > 1:
            raise ValueError("candles must belong to one trading session date")
        if candle_dates and next(iter(candle_dates)) != status.session_date:
            raise ValueError("candle session date does not match context session")

        if candles[-1].session_phase is not None and candles[-1].session_phase is not status.phase:
            raise ValueError("latest candle session phase does not match context session")

        return MarketContextSnapshot(
            instrument=instrument,
            observed_at=context_time,
            session=status,
            regime=regime,
        )
