from datetime import datetime, timedelta, timezone
from decimal import Decimal

from advance_system.market.candle_engine import Candle
from advance_system.market.regime import MarketRegime, MarketRegimeEngine
from advance_system.market.structure import SwingPoint, SwingType


def candle(i: int, price: int) -> Candle:
    start = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc) + timedelta(minutes=i)
    value = Decimal(price)
    return Candle("NSE_EQ|TEST", start, start + timedelta(minutes=1), value, value + Decimal("0.5"), value - Decimal("0.5"), value, 100)


def test_insufficient_data_is_safe_default():
    observation = MarketRegimeEngine(minimum_candles=5).classify([candle(i, 100 + i) for i in range(3)])
    assert observation.regime is MarketRegime.INSUFFICIENT_DATA
    assert observation.confidence == Decimal("0")


def test_uptrend_requires_structure_and_price_progression():
    candles = [candle(i, 100 + i * 2) for i in range(20)]
    swings = [
        SwingPoint("NSE_EQ|TEST", candles[5].end, Decimal("112"), SwingType.HIGH, 5),
        SwingPoint("NSE_EQ|TEST", candles[8].end, Decimal("108"), SwingType.LOW, 8),
        SwingPoint("NSE_EQ|TEST", candles[12].end, Decimal("126"), SwingType.HIGH, 12),
        SwingPoint("NSE_EQ|TEST", candles[15].end, Decimal("120"), SwingType.LOW, 15),
    ]
    observation = MarketRegimeEngine(minimum_candles=20).classify(candles, swings)
    assert observation.regime is MarketRegime.TREND_UP
    assert observation.trend_strength > 0


def test_compressed_prices_are_range():
    candles = [candle(i, 100) for i in range(20)]
    observation = MarketRegimeEngine(minimum_candles=20).classify(candles)
    assert observation.regime is MarketRegime.RANGE
    assert "compressed price range" in observation.evidence
