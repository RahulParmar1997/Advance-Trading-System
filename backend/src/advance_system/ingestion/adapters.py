from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import Protocol

from advance_system.domain.market_events import QuoteEvent
from advance_system.ingestion.normalizer import QuoteNormalizer, RawQuote


@dataclass(frozen=True, slots=True)
class Instrument:
    instrument: str
    exchange: str
    symbol: str
    asset_type: str


class MarketDataAdapter(Protocol):
    """Broker-neutral contract consumed by the ingestion layer."""

    async def stream_quotes(self, instruments: Sequence[Instrument]) -> AsyncIterator[RawQuote]:
        """Yield broker-shaped quotes; adapter owns transport details."""
        ...

    async def close(self) -> None:
        ...


class QuoteIngestionPipeline:
    """Normalizes adapter output without depending on a specific broker."""

    def __init__(self, adapter: MarketDataAdapter, normalizer: QuoteNormalizer | None = None) -> None:
        self.adapter = adapter
        self.normalizer = normalizer or QuoteNormalizer()

    async def stream(self, instruments: Sequence[Instrument]) -> AsyncIterator[QuoteEvent]:
        async for raw in self.adapter.stream_quotes(instruments):
            yield self.normalizer.normalize(raw)

    async def close(self) -> None:
        await self.adapter.close()
