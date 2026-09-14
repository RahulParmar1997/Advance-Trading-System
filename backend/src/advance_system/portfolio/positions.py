from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


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

    def unrealized_pnl(self, instrument: str, price: Decimal) -> Decimal:
        return self.get(instrument).mark_to_market(price)
