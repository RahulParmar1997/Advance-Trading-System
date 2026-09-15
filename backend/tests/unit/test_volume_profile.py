from datetime import datetime, timedelta, timezone
from decimal import Decimal

from advance_system.market.candle_engine import Candle
from advance_system.market.volume_profile import VolumeProfileConfig, VolumeProfileEngine


def candle(i: int, close: str, volume: int, session_date=None) -> Candle:
    start = datetime(2026, 1, 5, 9, 15, tzinfo=timezone.utc) + timedelta(minutes=i)
    return Candle("NSE_EQ|TEST", start, start + timedelta(minutes=1), Decimal(close), Decimal(close), Decimal(close), Decimal(close), volume, session_date, None)


def test_volume_profile_buckets_close_volume_and_finds_poc():
    candles = [candle(0, "100", 10), candle(1, "101", 30), candle(2, "100", 20)]
    profile = VolumeProfileEngine(VolumeProfileConfig(price_step=Decimal("1"))).build(candles)
    assert profile.total_volume == 60
    assert profile.point_of_control == Decimal("101")
    assert profile.levels == (profile.levels[0], profile.levels[1])
    assert [(x.price, x.volume) for x in profile.levels] == [(Decimal("100"), 30), (Decimal("101"), 30)]


def test_volume_profile_rejects_mixed_sessions_and_instruments():
    first = candle(0, "100", 10, datetime(2026, 1, 5).date())
    second = Candle("NSE_EQ|OTHER", first.start + timedelta(minutes=1), first.end + timedelta(minutes=1), Decimal("101"), Decimal("101"), Decimal("101"), Decimal("101"), 10, first.session_date, None)
    try:
        VolumeProfileEngine().build([first, second])
        assert False
    except ValueError as exc:
        assert "one instrument" in str(exc)

    second_same = candle(1, "101", 10, datetime(2026, 1, 6).date())
    try:
        VolumeProfileEngine().build([first, second_same])
        assert False
    except ValueError as exc:
        assert "session dates" in str(exc)
