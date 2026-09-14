from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

NORMAL_OPEN = "NORMAL_OPEN"


@dataclass(frozen=True, slots=True)
class MarketStatus:
    """Broker-neutral authoritative exchange status used by safety gates."""

    exchange: str
    status: str
    observed_at: datetime
    cas_status: str | None = None

    def validate(self) -> None:
        if not self.exchange.strip():
            raise ValueError("exchange is required")
        if not self.status.strip():
            raise ValueError("status is required")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.observed_at > datetime.now(timezone.utc):
            raise ValueError("observed_at cannot be in the future")

    @property
    def is_normal_open(self) -> bool:
        return self.status.strip().upper() == NORMAL_OPEN
