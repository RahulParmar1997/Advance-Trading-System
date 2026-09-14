from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class RejectionReason(StrEnum):
    RISK_DENIED = "RISK_DENIED"
    INSUFFICIENT_CASH = "INSUFFICIENT_CASH"
    INVALID_QUANTITY = "INVALID_QUANTITY"
    INVALID_PRICE = "INVALID_PRICE"
    NO_LIQUIDITY = "NO_LIQUIDITY"
    PARTICIPATION_LIMIT = "PARTICIPATION_LIMIT"


@dataclass(frozen=True, slots=True)
class BacktestRejection:
    timestamp: datetime
    instrument: str
    requested_quantity: int
    reason: RejectionReason


@dataclass(frozen=True, slots=True)
class HistoricalLiquidity:
    """Liquidity observable at the execution event; never inferred from future data."""

    available_quantity: int
    market_volume: int | None = None

    def validate(self) -> None:
        if self.available_quantity < 0:
            raise ValueError("available_quantity cannot be negative")
        if self.market_volume is not None and self.market_volume < 0:
            raise ValueError("market_volume cannot be negative")


class RejectionPolicy:
    """Deterministic pre-fill and participation rules for historical simulation."""

    def validate(self, quantity: int, price: object) -> RejectionReason | None:
        if quantity == 0:
            return RejectionReason.INVALID_QUANTITY
        if price <= 0:
            return RejectionReason.INVALID_PRICE
        return None

    def fill_quantity(
        self,
        requested_quantity: int,
        liquidity: HistoricalLiquidity,
        *,
        participation_rate: Decimal | None = None,
    ) -> tuple[int, RejectionReason | None]:
        liquidity.validate()
        quantity = abs(requested_quantity)
        if quantity == 0:
            return 0, RejectionReason.INVALID_QUANTITY
        if liquidity.available_quantity == 0:
            return 0, RejectionReason.NO_LIQUIDITY

        available = liquidity.available_quantity
        if participation_rate is not None:
            if not Decimal("0") < participation_rate <= Decimal("1"):
                raise ValueError("participation_rate must be in (0, 1]")
            if liquidity.market_volume is None:
                raise ValueError("market_volume is required when participation_rate is set")
            participation_cap = int(Decimal(liquidity.market_volume) * participation_rate)
            if participation_cap <= 0:
                return 0, RejectionReason.PARTICIPATION_LIMIT
            available = min(available, participation_cap)

        return min(quantity, available), None
