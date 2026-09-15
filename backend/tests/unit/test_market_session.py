from datetime import date, datetime, timezone

import pytest

from advance_system.market.session import IndiaMarketSession, SessionPhase, TradingDayCalendar


def session(holidays=None):
    return IndiaMarketSession(TradingDayCalendar(holidays))


def dt(hour, minute, *, day=14):
    return datetime(2026, 9, day, hour, minute, tzinfo=timezone.utc)


def test_regular_session_boundaries_are_inclusive_open_exclusive_close():
    calendar = session()
    assert calendar.status_at(datetime(2026, 9, 14, 3, 44, tzinfo=timezone.utc)).phase is SessionPhase.PRE_OPEN
    assert calendar.status_at(datetime(2026, 9, 14, 3, 45, tzinfo=timezone.utc)).phase is SessionPhase.OPEN
    assert calendar.status_at(datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)).phase is SessionPhase.POST_CLOSE


def test_pre_open_and_post_close_are_distinct():
    calendar = session()
    assert calendar.status_at(datetime(2026, 9, 14, 3, 30, tzinfo=timezone.utc)).phase is SessionPhase.PRE_OPEN
    assert calendar.status_at(datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)).phase is SessionPhase.POST_CLOSE


def test_weekend_and_injected_holiday_are_closed():
    calendar = session({date(2026, 9, 15)})
    assert calendar.status_at(dt(4, 0, day=13)).phase is SessionPhase.HOLIDAY
    assert calendar.status_at(dt(4, 0, day=15)).phase is SessionPhase.HOLIDAY


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        session().status_at(datetime(2026, 9, 14, 4, 0))


def test_assert_open_fails_closed_outside_regular_session():
    calendar = session()
    with pytest.raises(RuntimeError, match="market is not open"):
        calendar.assert_open(dt(3, 44))
    calendar.assert_open(dt(3, 45))
