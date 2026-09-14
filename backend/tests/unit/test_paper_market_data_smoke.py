from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.adapters.upstox.market_data import UpstoxQuote
from advance_system.domain.orders import Order, OrderSide, OrderStatus
from advance_system.ingestion.adapters import Instrument
from advance_system.ingestion.normalizer import RawQuote
from advance_system.ingestion.quality import DataQualityService
from advance_system.market.candle_engine import CandleEngine
from advance_system.oms.engine import PaperOMS
from advance_system.risk.engine import RiskEngine


class FakePaperAdapter:
    def __init__(self) -> None:
        self.closed = False

    async def stream_quotes(self, instruments):
        base = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)
        yield RawQuote(instruments[0].instrument, base, Decimal("100"), volume=1000)
        yield RawQuote(instruments[0].instrument, base.replace(second=30), Decimal("101"), volume=1010)
        yield RawQuote(instruments[0].instrument, base.replace(minute=16), Decimal("102"), volume=1030)

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_market_data_to_paper_order_vertical_slice():
    instrument = Instrument("NSE_EQ|TEST", "NSE", "TEST", "EQUITY")
    adapter = FakePaperAdapter()
    from advance_system.ingestion.adapters import QuoteIngestionPipeline

    pipeline = QuoteIngestionPipeline(adapter)
    quality = DataQualityService()
    candles = CandleEngine(interval_seconds=60)
    emitted = []
    now = datetime(2026, 1, 2, 9, 16, 1, tzinfo=timezone.utc)

    async for event in pipeline.stream([instrument]):
        observation = quality.observe(event, now=now)
        assert observation.accepted
        completed = candles.update(event)
        if completed is not None:
            emitted.append(completed)

    assert len(emitted) == 1
    assert emitted[0].open == Decimal("100")
    assert emitted[0].close == Decimal("101")
    assert emitted[0].volume == 10

    quote = await _last_quote(adapter, instrument)
    order = Order(
        order_id="paper-smoke-1",
        instrument=instrument.instrument,
        side=OrderSide.BUY,
        quantity=1,
        created_at=now,
    )
    decision = RiskEngine().check(order, quote)
    assert decision.allowed

    oms = PaperOMS()
    pending = oms.submit(order, decision)
    assert pending.status is OrderStatus.ORDER_PENDING
    filled = oms.paper_fill(order.order_id)
    assert filled.status is OrderStatus.FILLED
    await pipeline.close()
    assert adapter.closed


async def _last_quote(adapter, instrument):
    quotes = [quote async for quote in adapter.stream_quotes([instrument])]
    last = quotes[-1]
    return __import__("advance_system.domain.market_events", fromlist=["QuoteEvent"]).QuoteEvent(
        instrument=last.instrument,
        timestamp=last.timestamp,
        last_price=last.ltp,
        bid=last.bid,
        ask=last.ask,
        volume=last.volume,
    )
