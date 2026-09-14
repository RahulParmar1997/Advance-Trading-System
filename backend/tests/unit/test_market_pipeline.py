from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.domain.market_events import QuoteEvent
from advance_system.ingestion.normalizer import QuoteNormalizer, RawQuote
from advance_system.market.candle_engine import CandleEngine
from advance_system.market.features import FeatureEngine


def quote(second: int, price: str, volume: int) -> RawQuote:
    return RawQuote(
        instrument="NSE_EQ:TEST",
        timestamp=datetime(2026, 1, 1, 9, 15, second, tzinfo=timezone.utc),
        ltp=Decimal(price),
        volume=volume,
    )


def test_normalizer_produces_valid_canonical_event() -> None:
    event = QuoteNormalizer().normalize(quote(1, "100.25", 1000))
    assert isinstance(event, QuoteEvent)
    assert event.last_price == Decimal("100.25")
    event.validate()


def test_normalizer_rejects_naive_timestamp() -> None:
    raw = quote(1, "100", 100)
    raw = RawQuote(raw.instrument, raw.timestamp.replace(tzinfo=None), raw.ltp, volume=raw.volume)
    with pytest.raises(ValueError, match="timezone-aware"):
        QuoteNormalizer().normalize(raw)


def test_candle_closes_at_interval_boundary_and_uses_volume_delta() -> None:
    engine = CandleEngine(interval_seconds=60)
    engine.update(QuoteNormalizer().normalize(quote(10, "100", 1000)))
    engine.update(QuoteNormalizer().normalize(quote(30, "102", 1025)))
    completed = engine.update(QuoteNormalizer().normalize(quote(0, "101", 1100)).__class__(
        "NSE_EQ:TEST", datetime(2026, 1, 1, 9, 16, 0, tzinfo=timezone.utc), Decimal("101"), volume=1100
    ))
    assert completed is not None
    assert completed.open == Decimal("100")
    assert completed.high == Decimal("102")
    assert completed.low == Decimal("100")
    assert completed.close == Decimal("102")
    assert completed.volume == 25


def test_candle_rejects_out_of_order_events() -> None:
    engine = CandleEngine()
    normalizer = QuoteNormalizer()
    engine.update(normalizer.normalize(quote(30, "100", 100)))
    with pytest.raises(ValueError, match="out-of-order"):
        engine.update(normalizer.normalize(quote(20, "101", 110)))


def test_features_are_deterministic() -> None:
    engine = CandleEngine(interval_seconds=60)
    normalizer = QuoteNormalizer()
    engine.update(normalizer.normalize(quote(10, "100", 1000)))
    completed = engine.update(normalizer.normalize(
        RawQuote("NSE_EQ:TEST", datetime(2026, 1, 1, 9, 16, tzinfo=timezone.utc), Decimal("103"), volume=1010)
    ))
    assert completed is not None
    features = FeatureEngine().calculate(completed)
    assert features.range == Decimal("0")
    assert features.body == Decimal("0")
    assert features.direction == "FLAT"
