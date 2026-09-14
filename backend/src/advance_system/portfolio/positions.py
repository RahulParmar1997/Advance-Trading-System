from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from advance_system.risk.engine import RiskSnapshot


@dataclass(frozen=True, slots=True)
class Position:
    instrument: str
    quantity: int = 0
    average_price: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")

    def mark_to_market(self, price: Decimal) -> Decimal:
        if price <= 0:
            raise ValueError("price must be positive")
        return (price - self.average_price) * self.quantity


class PositionBook:
    """Deterministic long/short position accounting from executed fills."""

    def __init__(self) -> None:
        self._positions: dict[str, Position] = {}

    def apply_fill(self, instrument: str, quantity: int, price: Decimal) -> Position:
        if not instrument:
            raise ValueError("instrument is required")
        if quantity == 0 or price <= 0:
            raise ValueError("quantity must be non-zero and price must be positive")
        current = self._positions.get(instrument, Position(instrument))
        old_qty = current.quantity
        new_qty = old_qty + quantity
        realized = current.realized_pnl

        if old_qty == 0 or (old_qty > 0 and quantity > 0) or (old_qty < 0 and quantity < 0):
            total_abs = abs(old_qty) + abs(quantity)
            avg = ((abs(old_qty) * current.average_price) + (abs(quantity) * price)) / Decimal(total_abs)
        else:
            closing = min(abs(old_qty), abs(quantity))
            direction = Decimal("1") if old_qty > 0 else Decimal("-1")
            realized += (price - current.average_price) * closing * direction
            avg = Decimal("0") if new_qty == 0 else price

        updated = Position(instrument, new_qty, avg, realized)
        self._positions[instrument] = updated
        return updated

    def get(self, instrument: str) -> Position:
        return self._positions.get(instrument, Position(instrument))

    def instruments(self) -> tuple[str, ...]:
        return tuple(sorted(self._positions))

    def unrealized_pnl(self, instrument: str, price: Decimal) -> Decimal:
        return self.get(instrument).mark_to_market(price)

    def risk_snapshot(
        self,
        marks: dict[str, Decimal],
        *,
        daily_pnl: Decimal | None = None,
        strategy_pnl: Decimal | None = None,
        concurrent_trades: int | None = None,
        leverage: Decimal = Decimal("0"),
        broker_healthy: bool = True,
        kill_switch: bool = False,
        circuit_breaker: bool = False,
        available_liquidity: Decimal = Decimal("0"),
    ) -> RiskSnapshot:
        """Build an explicit RiskSnapshot from current positions and supplied account state.

        Mark prices are required for every non-flat position. P&L fields that cannot be
        derived from PositionBook (daily/strategy) remain caller-supplied instead of being
        guessed.
        """
        if leverage < 0 or available_liquidity < 0:
            raise ValueError("leverage and available liquidity cannot be negative")
        exposures: list[Decimal] = []
        for instrument, position in self._positions.items():
            if position.quantity == 0:
                continue
            price = marks.get(instrument)
            if price is None:
                raise ValueError(f"missing mark price for {instrument}")
            if price <= 0:
                raise ValueError("mark prices must be positive")
            exposures.append(abs(Decimal(position.quantity) * price))
        symbol_exposure = max(exposures, default=Decimal("0"))
        portfolio_exposure = sum(exposures, Decimal("0"))
        return RiskSnapshot(
            daily_pnl=Decimal("0") if daily_pnl is None else daily_pnl,
            strategy_pnl=Decimal("0") if strategy_pnl is None else strategy_pnl,
            symbol_exposure=symbol_exposure,
            portfolio_exposure=portfolio_exposure,
            concurrent_trades=sum(1 for position in self._positions.values() if position.quantity != 0)
            if concurrent_trades is None else concurrent_trades,
            leverage=leverage,
            broker_healthy=broker_healthy,
            kill_switch=kill_switch,
            circuit_breaker=circuit_breaker,
            available_liquidity=available_liquidity,
        )
