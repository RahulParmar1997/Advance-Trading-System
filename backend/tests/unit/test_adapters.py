from collections.abc import AsyncIterator, Sequence
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.ingestion.adapters import Instrument, MarketDataAdapter, QuoteIngestionPipeline
from advance_system.ingestion.normalizer import RawQuote


class FakeAdapter:
    def __init__(self) -> None:
        self.closed = False

    async def stream_quotes(self, instruments: Sequence[Instrument]) -> AsyncIterator[RawQuote]:
        assert instruments[0].symbol == "TEST"
        yield RawQuote("NSE_EQ|TEST", datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc), Decimal("101"))

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_pipeline_is_broker_neutral():
    adapter: MarketDataAdapter = FakeAdapter()
    pipeline = QuoteIngestionPipeline(adapter)
    events = [event async for event in pipeline.stream([Instrument("NSE_EQ|TEST", "NSE", "TEST", "EQUITY")])]
    await pipeline.close()
    assert len(events) == 1
    assert events[0].instrument == "NSE_EQ|TEST"
    assert events[0].last_price == Decimal("101")
    assert adapter.closed
