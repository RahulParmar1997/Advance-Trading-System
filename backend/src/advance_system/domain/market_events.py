from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class QuoteEvent:
    """Broker-neutral canonical quote event."""

    instrument: str
    timestamp: datetime
    last_price: Decimal
    bid: Decimal | None = None
    ask: Decimal | None = None
    volume: int | None = None

    def validate(self) -> None:
        if not self.instrument:
            raise ValueError("instrument is required")
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        if self.last_price <= 0:
            raise ValueError("last_price must be positive")
        if self.bid is not None and self.bid < 0:
            raise ValueError("bid cannot be negative")
        if self.ask is not None and self.ask < 0:
            raise ValueError("ask cannot be negative")
        if self.bid is not None and self.ask is not None and self.bid > self.ask:
            raise ValueError("bid cannot exceed ask")
        if self.volume is not None and self.volume < 0:
            raise ValueError("volume cannot be negative")
