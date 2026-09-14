from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class FillSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True, slots=True)
class BrokerFill:
    fill_id: str
    order_id: str
    instrument: str
    side: FillSide
    quantity: int
    price: Decimal
    timestamp: datetime

    def validate(self) -> None:
        if not self.fill_id or not self.order_id or not self.instrument:
            raise ValueError("fill_id, order_id and instrument are required")
        if self.quantity <= 0 or self.price <= 0:
            raise ValueError("fill quantity and price must be positive")
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")


@dataclass(frozen=True, slots=True)
class BrokerOrderSnapshot:
    order_id: str
    status: str
    filled_quantity: int
    average_fill_price: Decimal | None = None


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    order_id: str
    matched: bool
    reason: str


class ReconciliationEngine:
    """Broker-neutral comparison of canonical OMS fill state to broker state."""

    def reconcile(self, *, order_id: str, canonical_filled: int, broker: BrokerOrderSnapshot) -> ReconciliationResult:
        if not order_id or broker.order_id != order_id:
            return ReconciliationResult(order_id, False, "order identity mismatch")
        if canonical_filled < 0 or broker.filled_quantity < 0:
            return ReconciliationResult(order_id, False, "negative fill quantity")
        if canonical_filled != broker.filled_quantity:
            return ReconciliationResult(order_id, False, "filled quantity mismatch")
        return ReconciliationResult(order_id, True, "canonical and broker fill quantities match")
