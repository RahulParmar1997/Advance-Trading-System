from datetime import datetime, timedelta, timezone
from decimal import Decimal

from advance_system.market.candle_engine import Candle
from advance_system.market.liquidity import LiquidityDetector, LiquidityType


def c(i: int, o: str, h: str, low: str, close: str) -> Candle:
    start = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc) + timedelta(minutes=i)
    return Candle("NSE_EQ|TEST", start, start + timedelta(minutes=1), Decimal(o), Decimal(h), Decimal(low), Decimal(close), 0)


def test_equal_highs_and_lows_are_liquidity_levels():
    candles = [c(0, "10", "12", "8", "11"), c(1, "11", "12", "9", "10"), c(2, "10", "11", "8", "9")]
    detector = LiquidityDetector()
    highs = detector.equal_highs(candles)
    lows = detector.equal_lows(candles)
    assert highs[0].kind is LiquidityType.BUY_SIDE
    assert highs[0].price == Decimal("12")
    assert lows[0].kind is LiquidityType.SELL_SIDE


def test_three_candle_fvg_detection():
    candles = [c(0, "10", "11", "9", "10.5"), c(1, "11", "13", "10.5", "12.5"), c(2, "14", "15", "12", "14.5")]
    gaps = LiquidityDetector().fair_value_gaps(candles)
    assert len(gaps) == 1
    assert gaps[0].direction == "UP"
    assert gaps[0].lower == Decimal("11")
    assert gaps[0].upper == Decimal("12")


def test_order_block_uses_prior_opposite_candle():
    candles = [c(0, "11", "12", "9", "9.5"), c(1, "9.5", "14", "9", "13")]
    blocks = LiquidityDetector().order_blocks(candles)
    assert len(blocks) == 1
    assert blocks[0].direction == "UP"
    assert blocks[0].lower == Decimal("9")
    assert blocks[0].upper == Decimal("12")
