from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.domain.market_events import QuoteEvent
from advance_system.market.candle_engine import MultiTimeframeCandleEngine


def quote(second: int, price: str, volume: int) -> QuoteEvent:
    return QuoteEvent(
        instrument="NSE_EQ|TEST",
        timestamp=datetime(2026, 9, 14, 3, 45, tzinfo=timezone.utc) + timedelta(seconds=second),
        last_price=Decimal(price),
        volume=volume,
    )


def test_multiple_intervals_complete_independently():
    engine = MultiTimeframeCandleEngine((60, 300))
    assert engine.update(quote(0, "100", 100)) == {}
    assert engine.update(quote(30, "101", 120)) == {}

    completed = engine.update(quote(60, "102", 150))
    assert set(completed) == {60}
    assert completed[60].open == Decimal("100")
    assert completed[60].high == Decimal("101")
    assert completed[60].close == Decimal("101")
    assert completed[60].volume == 20

    completed = engine.update(quote(300, "105", 250))
    assert set(completed) == {60, 300}
    assert completed[60].close == Decimal("102")
    assert completed[60].volume == 30
    assert completed[300].open == Decimal("100")
    assert completed[300].high == Decimal("102")
    assert completed[300].close == Decimal("102")
    assert completed[300].volume == 50


def test_duplicate_intervals_are_deduplicated_and_invalid_intervals_rejected():
    assert MultiTimeframeCandleEngine((60, 60, 300)).intervals_seconds == (60, 300)
    with pytest.raises(ValueError, match="at least one"):
        MultiTimeframeCandleEngine(())
    with pytest.raises(ValueError, match="positive"):
        MultiTimeframeCandleEngine((60, 0))
