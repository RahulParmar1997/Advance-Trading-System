from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from advance_system.domain.market_events import QuoteEvent


@dataclass(frozen=True, slots=True)
class RawQuote:
    """Minimal broker adapter payload accepted by the normalization boundary."""

    instrument: str
    timestamp: datetime
    ltp: Decimal
    bid: Decimal | None = None
    ask: Decimal | None = None
    volume: int | None = None


class QuoteNormalizer:
    """Convert broker-shaped quote data into the canonical domain contract."""

    def normalize(self, raw: RawQuote) -> QuoteEvent:
        event = QuoteEvent(
            instrument=raw.instrument,
            timestamp=raw.timestamp,
            last_price=raw.ltp,
            bid=raw.bid,
            ask=raw.ask,
            volume=raw.volume,
        )
        event.validate()
        return event
