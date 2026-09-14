from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RejectionReason(StrEnum):
    RISK_DENIED = "RISK_DENIED"
    INSUFFICIENT_CASH = "INSUFFICIENT_CASH"
    INVALID_QUANTITY = "INVALID_QUANTITY"
    INVALID_PRICE = "INVALID_PRICE"
    NO_LIQUIDITY = "NO_LIQUIDITY"


@dataclass(frozen=True, slots=True)
class BacktestRejection:
    timestamp: object
    instrument: str
    requested_quantity: int
    reason: RejectionReason


class RejectionPolicy:
    """Deterministic pre-fill rejection rules for historical simulation."""

    def validate(self, quantity: int, price: object) -> RejectionReason | None:
        if quantity == 0:
            return RejectionReason.INVALID_QUANTITY
        if price <= 0:
            return RejectionReason.INVALID_PRICE
        return None
