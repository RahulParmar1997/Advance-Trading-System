from datetime import datetime, timedelta, timezone
from decimal import Decimal

from advance_system.domain.market_events import QuoteEvent
from advance_system.ingestion.quality import DataQualityCode, QuoteQualityGate


BASE = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)


def quote(**overrides) -> QuoteEvent:
    values = {
        "instrument": "NSE_EQ|INE009A01021",
        "timestamp": BASE,
        "last_price": Decimal("100.00"),
        "volume": 100,
    }
    values.update(overrides)
    return QuoteEvent(**values)


def test_accepts_fresh_quote_and_tracks_volume() -> None:
    gate = QuoteQualityGate(max_age=timedelta(seconds=10))
    result = gate.evaluate(quote(), now=BASE + timedelta(seconds=5))
    assert result.accepted is True
    assert result.code == DataQualityCode.VALID


def test_rejects_stale_quote() -> None:
    gate = QuoteQualityGate(max_age=timedelta(seconds=10))
    result = gate.evaluate(quote(), now=BASE + timedelta(seconds=11))
    assert result.code == DataQualityCode.STALE


def test_rejects_duplicate_quote() -> None:
    gate = QuoteQualityGate()
    now = BASE + timedelta(seconds=1)
    assert gate.evaluate(quote(), now=now).accepted
    result = gate.evaluate(quote(), now=now)
    assert result.code == DataQualityCode.DUPLICATE


def test_rejects_out_of_order_quote() -> None:
    gate = QuoteQualityGate()
    assert gate.evaluate(quote(timestamp=BASE + timedelta(seconds=2)), now=BASE + timedelta(seconds=3)).accepted
    result = gate.evaluate(quote(timestamp=BASE + timedelta(seconds=1)), now=BASE + timedelta(seconds=3))
    assert result.code == DataQualityCode.OUT_OF_ORDER


def test_rejects_cumulative_volume_regression() -> None:
    gate = QuoteQualityGate()
    assert gate.evaluate(quote(volume=100), now=BASE + timedelta(seconds=1)).accepted
    result = gate.evaluate(quote(timestamp=BASE + timedelta(seconds=1), volume=99), now=BASE + timedelta(seconds=2))
    assert result.code == DataQualityCode.VOLUME_REGRESSION


def test_rejects_future_event() -> None:
    gate = QuoteQualityGate()
    result = gate.evaluate(quote(timestamp=BASE + timedelta(seconds=2)), now=BASE + timedelta(seconds=1))
    assert result.code == DataQualityCode.INVALID


def test_requires_timezone_aware_timestamps() -> None:
    gate = QuoteQualityGate()
    result = gate.evaluate(quote(timestamp=datetime(2026, 1, 2, 9, 15)), now=BASE)
    assert result.code == DataQualityCode.INVALID
