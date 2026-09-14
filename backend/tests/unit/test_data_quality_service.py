from datetime import datetime, timedelta, timezone
from decimal import Decimal

from advance_system.domain.market_events import QuoteEvent
from advance_system.ingestion.data_quality import DataQualityService

BASE = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)


def q(ts=BASE):
    return QuoteEvent("NSE_EQ|TEST", ts, Decimal("100"))


def test_gap_is_observable_but_quote_is_accepted():
    service = DataQualityService(max_age=timedelta(seconds=60), max_gap=timedelta(seconds=10))
    assert service.observe(q(), now=BASE + timedelta(seconds=1)).code == "VALID"
    result = service.observe(q(BASE + timedelta(seconds=20)), now=BASE + timedelta(seconds=21))
    assert result.accepted
    assert result.code == "GAP"


def test_duplicate_timestamp_is_rejected():
    service = DataQualityService(max_age=timedelta(seconds=60))
    assert service.observe(q(), now=BASE + timedelta(seconds=1)).accepted
    result = service.observe(q(), now=BASE + timedelta(seconds=2))
    assert not result.accepted
    assert result.code == "DUPLICATE"


def test_out_of_order_is_rejected():
    service = DataQualityService(max_age=timedelta(seconds=60))
    service.observe(q(BASE + timedelta(seconds=5)), now=BASE + timedelta(seconds=6))
    result = service.observe(q(BASE + timedelta(seconds=4)), now=BASE + timedelta(seconds=6))
    assert not result.accepted
    assert result.code == "OUT_OF_ORDER"


def test_stale_and_future_events_are_rejected():
    service = DataQualityService(max_age=timedelta(seconds=10))
    stale = service.observe(q(), now=BASE + timedelta(seconds=11))
    future = service.observe(q(BASE + timedelta(seconds=2)), now=BASE + timedelta(seconds=1))
    assert stale.code == "STALE"
    assert future.code == "FUTURE"
