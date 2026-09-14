from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from enum import StrEnum
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


class SessionPhase(StrEnum):
    CLOSED = "closed"
    PRE_OPEN = "pre_open"
    OPEN = "open"
    POST_CLOSE = "post_close"
    HOLIDAY = "holiday"


class TradingDayCalendar:
    """Injectable exchange-calendar boundary. Weekends are closed by default."""

    def __init__(self, holidays: set[date] | None = None) -> None:
        self._holidays = frozenset(holidays or set())

    def is_trading_day(self, session_date: date) -> bool:
        return session_date.weekday() < 5 and session_date not in self._holidays


@dataclass(frozen=True, slots=True)
class MarketSessionStatus:
    phase: SessionPhase
    session_date: date
    timezone: str = "Asia/Kolkata"

    @property
    def is_open(self) -> bool:
        return self.phase is SessionPhase.OPEN


@dataclass(frozen=True, slots=True)
class IndiaMarketSession:
    """Deterministic NSE/BSE regular-session gate with injectable holidays."""

    calendar: TradingDayCalendar
    pre_open_start: time = time(9, 0)
    open_time: time = time(9, 15)
    close_time: time = time(15, 30)
    post_close_end: time = time(16, 0)
    timezone: ZoneInfo = IST

    def status_at(self, at: datetime) -> MarketSessionStatus:
        if at.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        local = at.astimezone(self.timezone)
        session_date = local.date()
        if not self.calendar.is_trading_day(session_date):
            return MarketSessionStatus(SessionPhase.HOLIDAY, session_date)
        current = local.time()
        if current < self.pre_open_start:
            phase = SessionPhase.CLOSED
        elif current < self.open_time:
            phase = SessionPhase.PRE_OPEN
        elif current < self.close_time:
            phase = SessionPhase.OPEN
        elif current < self.post_close_end:
            phase = SessionPhase.POST_CLOSE
        else:
            phase = SessionPhase.CLOSED
        return MarketSessionStatus(phase, session_date)

    def assert_open(self, at: datetime) -> None:
        status = self.status_at(at)
        if not status.is_open:
            raise RuntimeError(f"market is not open: {status.phase.value}")
