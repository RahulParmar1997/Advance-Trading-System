from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.market.candle_engine import Candle
from advance_system.market.context import MarketContextEngine
from advance_system.market.regime import MarketRegimeEngine
from advance_system.market.session import IndiaMarketSession, SessionPhase, TradingDayCalendar


def candle(index: int, close: str, *, phase: SessionPhase = SessionPhase.OPEN) -> Candle:
    start = datetime(2026, 9, 15, 3, 45 + index, tzinfo=timezone.utc)
    return Candle(
        "NSE_EQ|TEST",
        start,
        start + timedelta(minutes=1),
        Decimal(close),
        Decimal(close),
        Decimal(close),
        Decimal(close),
        100,
        datetime(2026, 9, 15, tzinfo=timezone.utc).date(),
        phase,
    )


def test_context_joins_session_and_regime_from_completed_candles() -> None:
    engine = MarketContextEngine(
        IndiaMarketSession(TradingDayCalendar()),
        MarketRegimeEngine(minimum_candles=3),
    )
    snapshot = engine.build([candle(0, "100"), candle(1, "102"), candle(2, "104")])
    assert snapshot.instrument == "NSE_EQ|TEST"
    assert snapshot.session.phase is SessionPhase.OPEN
    assert snapshot.session.session_date.isoformat() == "2026-09-15"
    assert snapshot.regime_available
    assert snapshot.confidence >= Decimal("0")


def test_context_rejects_future_observation_and_mixed_instruments() -> None:
    engine = MarketContextEngine(IndiaMarketSession(TradingDayCalendar()), MarketRegimeEngine(minimum_candles=2))
    candles = [candle(0, "100"), candle(1, "101")]
    with pytest.raises(ValueError, match="cannot precede"):
        engine.build(candles, observed_at=candles[-1].end - timedelta(seconds=1))
    with pytest.raises(ValueError, match="one instrument"):
        engine.build([candles[0], Candle("NSE_EQ|OTHER", candles[1].start, candles[1].end, Decimal("101"), Decimal("101"), Decimal("101"), Decimal("101"), 100, candles[1].session_date, SessionPhase.OPEN)])


def test_context_rejects_session_date_mismatch() -> None:
    engine = MarketContextEngine(IndiaMarketSession(TradingDayCalendar()), MarketRegimeEngine(minimum_candles=2))
    first = candle(0, "100")
    second = Candle(
        "NSE_EQ|TEST",
        candle(1, "101").start,
        candle(1, "101").end,
        Decimal("101"),
        Decimal("101"),
        Decimal("101"),
        Decimal("101"),
        100,
        datetime(2026, 9, 14, tzinfo=timezone.utc).date(),
        SessionPhase.OPEN,
    )
    with pytest.raises(ValueError, match="one trading session date"):
        engine.build([first, second])
