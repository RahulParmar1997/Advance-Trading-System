from datetime import date, datetime, timezone

import pytest

from advance_system.market.instrument_master import InstrumentMaster, InstrumentRecord
from advance_system.market.session import IndiaMarketSession, TradingDayCalendar


def test_instrument_master_rejects_unknown_and_inactive_symbols():
    master = InstrumentMaster([
        InstrumentRecord("NSE_EQ|ABC", "NSE", "ABC", "EQUITY"),
        InstrumentRecord("NSE_EQ|OLD", "NSE", "OLD", "EQUITY", is_active=False),
    ])
    assert master.contains_active("NSE_EQ|ABC")
    assert not master.contains_active("NSE_EQ|OLD")
    with pytest.raises(KeyError):
        master.require_active("NSE_EQ|UNKNOWN")
    with pytest.raises(ValueError):
        master.require_active("NSE_EQ|OLD")


def test_nse_session_uses_india_time_and_excludes_close():
    session = IndiaMarketSession(TradingDayCalendar())
    assert session.status_at(datetime(2026, 1, 2, 3, 45, tzinfo=timezone.utc)).is_open
    assert not session.status_at(datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)).is_open
    assert not session.status_at(datetime(2026, 1, 2, 3, 30, tzinfo=timezone.utc)).is_open


def test_calendar_is_injectable():
    holiday = date(2026, 1, 2)
    calendar = TradingDayCalendar({holiday})
    assert not calendar.is_trading_day(holiday)
