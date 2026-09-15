from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Sequence


class Aggressor(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class TradePrint:
    instrument: str
    timestamp: datetime
    price: Decimal
    quantity: int
    aggressor: Aggressor

    def validate(self) -> None:
        if not self.instrument.strip():
            raise ValueError("instrument is required")
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        if self.price <= 0:
            raise ValueError("price must be positive")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")


@dataclass(frozen=True, slots=True)
class OrderFlowSummary:
    instrument: str
    buy_volume: int
    sell_volume: int
    unknown_volume: int
    delta: int
    cumulative_delta: int


class OrderFlowEngine:
    """Aggregate explicit trade prints; never invents aggressor side from quotes."""

    def summarize(self, trades: Sequence[TradePrint]) -> OrderFlowSummary:
        if not trades:
            raise ValueError("trades cannot be empty")
        instrument = trades[0].instrument
        buy = sell = unknown = 0
        previous_timestamp: datetime | None = None
        for trade in trades:
            trade.validate()
            if trade.instrument != instrument:
                raise ValueError("order flow requires one instrument")
            if previous_timestamp is not None and trade.timestamp < previous_timestamp:
                raise ValueError("trades must be chronological")
            previous_timestamp = trade.timestamp
            if trade.aggressor is Aggressor.BUY:
                buy += trade.quantity
            elif trade.aggressor is Aggressor.SELL:
                sell += trade.quantity
            else:
                unknown += trade.quantity
        delta = buy - sell
        return OrderFlowSummary(instrument, buy, sell, unknown, delta, delta)

    @staticmethod
    def infer_aggressor(price: Decimal, bid: Decimal | None, ask: Decimal | None) -> Aggressor:
        """Infer side only on an exact bid/ask match; otherwise remain UNKNOWN."""
        if price <= 0:
            raise ValueError("price must be positive")
        if bid is not None and bid < 0:
            raise ValueError("bid cannot be negative")
        if ask is not None and ask < 0:
            raise ValueError("ask cannot be negative")
        if bid is not None and ask is not None and bid > ask:
            raise ValueError("bid cannot exceed ask")
        if ask is not None and price == ask:
            return Aggressor.BUY
        if bid is not None and price == bid:
            return Aggressor.SELL
        return Aggressor.UNKNOWN
