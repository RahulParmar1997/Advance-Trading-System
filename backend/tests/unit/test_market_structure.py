from datetime import datetime, timedelta, timezone
from decimal import Decimal

from advance_system.market.candle_engine import Candle
from advance_system.market.structure import MarketStructureEngine, SwingDetector, SwingType


def candle(i: int, high: str, low: str, close: str) -> Candle:
    start = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc) + timedelta(minutes=i)
    return Candle("NSE_EQ|TEST", start, start + timedelta(minutes=1), Decimal(close), Decimal(high), Decimal(low), Decimal(close), 0)


def test_confirmed_swing_high_and_low():
    candles = [
        candle(0, "10", "8", "9"),
        candle(1, "11", "8.5", "10"),
        candle(2, "15", "9", "14"),
        candle(3, "12", "8", "8"),
        candle(4, "11", "7", "7"),
        candle(5, "10", "8", "9"),
    ]
    swings = SwingDetector(left=1, right=1).detect(candles)
    assert any(s.kind is SwingType.HIGH and s.price == Decimal("15") for s in swings)
    assert any(s.kind is SwingType.LOW and s.price == Decimal("7") for s in swings)


def test_swing_labels_are_deterministic():
    candles = [
        candle(0, "10", "8", "9"),
        candle(1, "12", "9", "11"),
        candle(2, "9", "6", "7"),
        candle(3, "14", "8", "13"),
        candle(4, "10", "5", "6"),
        candle(5, "15", "7", "14"),
    ]
    swings = SwingDetector(left=1, right=1).detect(candles)
    labels = MarketStructureEngine().classify_swings(swings)
    assert labels == ["H", "L", "HH", "LL"]


def test_break_of_structure_emits_directional_signal():
    candles = [
        candle(0, "10", "8", "9"),
        candle(1, "12", "9", "11"),
        candle(2, "10", "7", "8"),
        candle(3, "11", "7", "9"),
        candle(4, "13", "8", "12.5"),
    ]
    swings = SwingDetector(left=1, right=1).detect(candles)
    signals = MarketStructureEngine().signals(candles, swings)
    assert any(signal.direction == "UP" for signal in signals)
