from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


@dataclass(frozen=True, slots=True)
class MarketSession:
    """Exchange-session policy. Holidays remain an injectable concern."""

    open_time: time = time(9, 15)
    close_time: time = time(15, 30)
    timezone: ZoneInfo = IST

    def is_open(self, at: datetime, *, trading_day: bool = True) -> bool:
        if not trading_day:
            return False
        local = at.astimezone(self.timezone)
        return self.open_time <= local.time() < self.close_time


class TradingDayCalendar:
    """Minimal injectable calendar boundary; no holiday assumptions in domain logic."""

    def __init__(self, holidays: set[object] | None = None) -> None:
        self._holidays = holidays or set()

    def is_trading_day(self, at: datetime) -> bool:
        return at.astimezone(IST).date() not in self._holidays
