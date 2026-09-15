from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Protocol, Sequence

from advance_system.backtest.rejections import HistoricalLiquidity, RejectionPolicy
from advance_system.domain.versioning import ContractName, validate_contract_version


@dataclass(frozen=True, slots=True)
class BacktestEvent:
    timestamp: datetime
    instrument: str
    price: Decimal
    liquidity: HistoricalLiquidity | None = None
    contract_version: int = 1

    def validate(self) -> None:
        validate_contract_version(ContractName.BACKTEST_EVENT, self.contract_version)
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        if not self.instrument or self.price <= 0:
            raise ValueError("instrument and positive price are required")
        if self.liquidity is not None:
            self.liquidity.validate()


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
    ending_position: int = 0
    ending_equity: Decimal = Decimal("0")
    max_drawdown: Decimal = Decimal("0")
    rejected_orders: int = 0


class BacktestStrategy(Protocol):
    def on_event(self, event: BacktestEvent) -> int:
        """Return signed position delta; zero means no order."""


@dataclass(frozen=True, slots=True)
class FillPolicy:
    fee_bps: Decimal = Decimal("0")
    slippage_bps: Decimal = Decimal("0")
    latency: timedelta = timedelta(0)
    max_fill_quantity: int | None = None
    participation_rate: Decimal | None = None

    def validate(self) -> None:
        if self.fee_bps < 0 or self.slippage_bps < 0:
            raise ValueError("execution costs cannot be negative")
        if self.latency < timedelta(0):
            raise ValueError("latency cannot be negative")
        if self.max_fill_quantity is not None and self.max_fill_quantity <= 0:
            raise ValueError("max_fill_quantity must be positive")
        if self.participation_rate is not None and not Decimal("0") < self.participation_rate <= Decimal("1"):
            raise ValueError("participation_rate must be in (0, 1]")


class EventDrivenBacktester:
    """Deterministic event-driven PAPER backtester with observable liquidity limits."""

    def run(
        self,
        events: Sequence[BacktestEvent],
        strategy: BacktestStrategy,
        *,
        starting_cash: Decimal,
        fee_bps: Decimal = Decimal("0"),
        slippage_bps: Decimal = Decimal("0"),
        latency: timedelta = timedelta(0),
        max_fill_quantity: int | None = None,
        participation_rate: Decimal | None = None,
    ) -> BacktestResult:
        policy = FillPolicy(fee_bps, slippage_bps, latency, max_fill_quantity, participation_rate)
        policy.validate()
        if starting_cash < 0:
            raise ValueError("starting cash cannot be negative")
        ordered = tuple(sorted(events, key=lambda event: event.timestamp))
        for event in ordered:
            event.validate()

        cash = starting_cash
        position = 0
        average = Decimal("0")
        realized = Decimal("0")
        fills: list[BacktestFill] = []
        rejected = 0
        equity_peak = starting_cash
        max_drawdown = Decimal("0")
        last_price = Decimal("0")
        rejection_policy = RejectionPolicy()

        for index, event in enumerate(ordered):
            last_price = event.price
            delta = strategy.on_event(event)
            if delta == 0:
                equity = cash + Decimal(position) * event.price
                equity_peak = max(equity_peak, equity)
                max_drawdown = max(max_drawdown, equity_peak - equity)
                continue

            rejection = rejection_policy.validate(delta, event.price)
            if rejection is not None:
                rejected += 1
                continue

            execution_time = event.timestamp + policy.latency
            execution_event = next(
                (candidate for candidate in ordered[index:] if candidate.timestamp >= execution_time),
                None,
            )
            if execution_event is None:
                rejected += 1
                continue

            remaining = abs(delta)
            execution_index = ordered.index(execution_event, index)
            while remaining > 0 and execution_event is not None:
                explicit_liquidity = execution_event.liquidity is not None
                liquidity = execution_event.liquidity or HistoricalLiquidity(remaining)
                fill_qty, liquidity_rejection = rejection_policy.fill_quantity(
                    delta if delta > 0 else -remaining,
                    liquidity,
                    participation_rate=policy.participation_rate,
                )
                if policy.max_fill_quantity is not None:
                    fill_qty = min(fill_qty, policy.max_fill_quantity)

                if liquidity_rejection is not None or fill_qty <= 0:
                    rejected += 1
                    break

                direction = Decimal("1") if delta > 0 else Decimal("-1")
                execution_price = execution_event.price * (
                    Decimal("1") + direction * policy.slippage_bps / Decimal("10000")
                )
                notional = execution_price * fill_qty
                fee = notional * policy.fee_bps / Decimal("10000")
                if delta > 0 and cash < notional + fee:
                    rejected += 1
                    break
                if delta > 0:
                    cash -= notional + fee
                else:
                    cash += notional - fee

                old_position = position
                signed_qty = fill_qty if delta > 0 else -fill_qty
                if old_position == 0 or (old_position > 0 and signed_qty > 0) or (old_position < 0 and signed_qty < 0):
                    total = abs(old_position) + fill_qty
                    average = ((abs(old_position) * average) + fill_qty * execution_price) / Decimal(total)
                else:
                    closing = min(abs(old_position), fill_qty)
                    direction_old = Decimal("1") if old_position > 0 else Decimal("-1")
                    realized += (execution_price - average) * closing * direction_old - fee
                    if old_position + signed_qty == 0:
                        average = Decimal("0")
                    elif abs(signed_qty) > abs(old_position):
                        average = execution_price
                position += signed_qty
                fills.append(BacktestFill(execution_event.timestamp, event.instrument, fill_qty, execution_price, fee))
                remaining -= fill_qty

                if remaining <= 0:
                    break
                if not explicit_liquidity and policy.max_fill_quantity is not None:
                    continue
                execution_index += 1
                execution_event = ordered[execution_index] if execution_index < len(ordered) else None
                if execution_event is None:
                    rejected += 1
                    break

            equity = cash + Decimal(position) * event.price
            equity_peak = max(equity_peak, equity)
            max_drawdown = max(max_drawdown, equity_peak - equity)

        ending_equity = cash + Decimal(position) * last_price if last_price else cash
        return BacktestResult(tuple(fills), realized, cash, position, ending_equity, max_drawdown, rejected)
