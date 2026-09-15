from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.market.candle_engine import Candle
from advance_system.market.market_state import MarketStateEngine


def c(i: int, o: str, h: str, low: str, close: str) -> Candle:
    start = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc) + timedelta(minutes=i)
    return Candle("NSE_EQ|TEST", start, start + timedelta(minutes=1), Decimal(o), Decimal(h), Decimal(low), Decimal(close), 0)


def test_market_state_composes_structure_and_liquidity():
    candles = [
        c(0, "10", "11", "9", "9.5"),
        c(1, "9.5", "12", "9", "11.5"),
        c(2, "11.5", "14", "12", "13.5"),
        c(3, "13.5", "13", "8", "9"),
        c(4, "9", "15", "8.5", "14"),
    ]
    state = MarketStateEngine(swing_left=1, swing_right=1).build(candles, timeframe_seconds=60)
    assert state.instrument == "NSE_EQ|TEST"
    assert state.timeframe_seconds == 60
    assert len(state.candles) == 5
    assert state.swings
    assert state.fair_value_gaps
    assert state.order_blocks


def test_market_state_rejects_mixed_instruments():
    first = c(0, "10", "11", "9", "10")
    second = Candle("NSE_EQ|OTHER", first.start, first.end, first.open, first.high, first.low, first.close, 0)
    with pytest.raises(ValueError, match="one instrument"):
        MarketStateEngine().build([first, second], timeframe_seconds=60)
