from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Literal

DataQuality = Literal["HEALTHY", "DEGRADED", "STALE", "INVALID"]


@dataclass(frozen=True)
class QuoteEvent:
    instrument_id: str
    timestamp: datetime
    ltp: Decimal
    bid: Decimal | None = None
    ask: Decimal | None = None
    bid_qty: int | None = None
    ask_qty: int | None = None
    volume: int | None = None
    quality: DataQuality = "HEALTHY"


@dataclass(frozen=True)
class MarketStatusEvent:
    timestamp: datetime
    session: str
    status: str


@dataclass(frozen=True)
class NormalizedMarketState:
    instrument_id: str
    timestamp: datetime
    ltp: Decimal
    quality: DataQuality
