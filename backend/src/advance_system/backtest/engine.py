from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol, Sequence


@dataclass(frozen=True, slots=True)
class BacktestEvent:
    timestamp: datetime
    instrument: str
    price: Decimal

    def validate(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        if not self.instrument or self.price <= 0:
            raise ValueError("instrument and positive price are required")


@dataclass(frozen=True, slots=True)
class BacktestFill:
    timestamp: datetime
    instrument: str
    quantity: int
    price: Decimal
    fee: Decimal = Decimal("0")


@dataclass(frozen=True, slots=True)
class BacktestResult:
    fills: tuple[BacktestFill, ...]
    realized_pnl: Decimal
    ending_cash: Decimal


class BacktestStrategy(Protocol):
    def on_event(self, event: BacktestEvent) -> int:
        """Return signed target quantity delta; zero means no order."""


class EventDrivenBacktester:
    """Deterministic event-driven PAPER backtester; events are sorted before execution."""

    def run(
        self,
        events: Sequence[BacktestEvent],
        strategy: BacktestStrategy,
        *,
        starting_cash: Decimal,
        fee_bps: Decimal = Decimal("0"),
        slippage_bps: Decimal = Decimal("0"),
    ) -> BacktestResult:
        if starting_cash < 0 or fee_bps < 0 or slippage_bps < 0:
            raise ValueError("cash and execution costs cannot be negative")
        ordered = tuple(sorted(events, key=lambda event: event.timestamp))
        if any(event.timestamp.tzinfo is None for event in ordered):
            raise ValueError("timestamps must be timezone-aware")
        if any(ordered[i].timestamp > ordered[i + 1].timestamp for i in range(len(ordered) - 1)):
            raise ValueError("events must be chronologically ordered")

        cash = starting_cash
        fills: list[BacktestFill] = []
        position = 0
        average = Decimal("0")
        realized = Decimal("0")

        for event in ordered:
            event.validate()
            delta = strategy.on_event(event)
            if delta == 0:
                continue
            execution_price = event.price * (Decimal("1") + (slippage_bps / Decimal("10000") * (Decimal("1") if delta > 0 else Decimal("-1"))))
            quantity = abs(delta)
            notional = execution_price * quantity
            fee = notional * fee_bps / Decimal("10000")
            signed = Decimal(quantity if delta > 0 else -quantity)
            if signed > 0:
                cash -= notional + fee
            else:
                cash += notional - fee
            if position == 0 or (position > 0 and delta > 0) or (position < 0 and delta < 0):
                total = abs(position) + quantity
                average = ((abs(position) * average) + (quantity * execution_price)) / Decimal(total)
            else:
                closing = min(abs(position), quantity)
                direction = Decimal("1") if position > 0 else Decimal("-1")
                realized += (execution_price - average) * closing * direction - fee
                if position + delta == 0:
                    average = Decimal("0")
                elif abs(delta) > abs(position):
                    average = execution_price
            position += delta
            fills.append(BacktestFill(event.timestamp, event.instrument, quantity, execution_price, fee))

        return BacktestResult(tuple(fills), realized, cash)
