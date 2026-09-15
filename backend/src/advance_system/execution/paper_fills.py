from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from advance_system.oms.idempotency import PaperOrderGateway
from advance_system.oms.state_machine import OmsState
from advance_system.portfolio.positions import PositionBook


@dataclass(frozen=True, slots=True)
class PaperFill:
    order_id: str
    instrument: str
    quantity: int
    price: Decimal


class PaperFillSimulator:
    """Explicit PAPER-only fill path; no broker/network side effects."""

    def __init__(self, gateway: PaperOrderGateway, positions: PositionBook | None = None) -> None:
        self._gateway = gateway
        self._positions = positions or PositionBook()

    def fill(self, order_id: str, price: Decimal, *, quantity: int | None = None) -> PaperFill:
        order = self._gateway.get(order_id)
        if price <= 0:
            raise ValueError("fill price must be positive")
        fill_qty = order.quantity if quantity is None else quantity
        if fill_qty <= 0 or fill_qty > order.quantity - order.filled_quantity:
            raise ValueError("fill quantity exceeds remaining order quantity")

        new_filled = order.filled_quantity + fill_qty
        target = OmsState.FILLED if new_filled == order.quantity else OmsState.PARTIALLY_FILLED
        self._gateway.transition(order_id, target, filled_quantity=new_filled)

        signed_qty = fill_qty if order.quantity > 0 else -fill_qty
        position = self._positions.apply_fill(order.instrument, signed_qty, price)
        return PaperFill(order_id, position.instrument, fill_qty, price)

    @property
    def positions(self) -> PositionBook:
        return self._positions
