from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.domain.market_events import QuoteEvent
from advance_system.market.candle_engine import CandleEngine, MultiTimeframeCandleEngine
from advance_system.market.session import IndiaMarketSession, TradingDayCalendar


def quote(minute: int, price: str, volume: int = 100) -> QuoteEvent:
    return QuoteEvent("NSE_EQ|TEST", datetime(2026, 9, 14, 3, minute, tzinfo=timezone.utc), Decimal(price), volume=volume)


def test_session_metadata_is_attached_to_completed_candle():
    engine = CandleEngine(60, IndiaMarketSession(TradingDayCalendar()))
    engine.update(quote(45, "100"))
    completed = engine.update(quote(46, "101", 110))
    assert completed is not None
    assert completed.session_date.isoformat() == "2026-09-14"
    assert completed.session_phase.value == "open"


def test_quotes_outside_regular_session_are_rejected():
    engine = CandleEngine(60, IndiaMarketSession(TradingDayCalendar()))
    with pytest.raises(ValueError, match="outside regular trading session"):
        engine.update(QuoteEvent("NSE_EQ|TEST", datetime(2026, 9, 14, 3, 30, tzinfo=timezone.utc), Decimal("100")))


def test_multi_timeframe_session_metadata_is_preserved():
    engine = MultiTimeframeCandleEngine((60, 300), IndiaMarketSession(TradingDayCalendar()))
    engine.update(quote(45, "100"))
    completed = engine.update(quote(50, "105", 150))
    assert set(completed) == {60, 300}
    assert all(candle.session_phase.value == "open" for candle in completed.values())


def test_session_date_change_cannot_merge_candles():
    # A custom calendar makes both dates valid; the session-aware engine still
    # refuses to merge different trading session dates.
    calendar = TradingDayCalendar()
    engine = CandleEngine(60, IndiaMarketSession(calendar))
    engine.update(quote(45, "100"))
    with pytest.raises(ValueError, match="outside regular trading session"):
        engine.update(QuoteEvent("NSE_EQ|TEST", datetime(2026, 9, 15, 3, 45, tzinfo=timezone.utc), Decimal("101")))
