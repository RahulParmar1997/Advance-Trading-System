from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol

from advance_system.ingestion.adapters import Instrument, MarketDataAdapter
from advance_system.ingestion.normalizer import RawQuote


@dataclass(frozen=True, slots=True)
class UpstoxQuote:
    instrument: str
    timestamp: datetime
    last_price: Decimal
    bid: Decimal | None = None
    ask: Decimal | None = None
    volume: int | None = None


class UpstoxMarketDataClient(Protocol):
    async def stream_quotes(self, instruments: Sequence[Instrument], access_token: str) -> AsyncIterator[UpstoxQuote]:
        ...

    async def close(self) -> None:
        ...


class UpstoxAdapter(MarketDataAdapter):
    """Translates Upstox-shaped data into the broker-neutral RawQuote contract."""

    def __init__(self, client: UpstoxMarketDataClient, token_provider) -> None:
        self.client = client
        self.token_provider = token_provider

    async def stream_quotes(self, instruments: Sequence[Instrument]) -> AsyncIterator[RawQuote]:
        token = await self.token_provider.get_access_token()
        async for quote in self.client.stream_quotes(instruments, token.value):
            yield RawQuote(
                instrument=quote.instrument,
                timestamp=quote.timestamp,
                ltp=quote.last_price,
                bid=quote.bid,
                ask=quote.ask,
                volume=quote.volume,
            )

    async def close(self) -> None:
        await self.client.close()
