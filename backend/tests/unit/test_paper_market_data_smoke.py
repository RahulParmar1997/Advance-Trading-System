from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.domain.market_status import MarketStatus
from advance_system.execution.paper_workflow import PaperExecutionWorkflow
from advance_system.ingestion.adapters import Instrument, QuoteIngestionPipeline
from advance_system.ingestion.normalizer import RawQuote
from advance_system.ingestion.quality import QuoteQualityGate
from advance_system.market.candle_engine import CandleEngine
from advance_system.oms.state_machine import OmsOrder, OmsState
from advance_system.risk.engine import RiskContext, RiskEngine, RiskPolicy, RiskSnapshot


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


class Opportunity:
    risk_reward = Decimal("2")


def risk_engine() -> RiskEngine:
    return RiskEngine(
        RiskPolicy(
            max_daily_loss=Decimal("100000"),
            max_strategy_loss=Decimal("50000"),
            max_symbol_exposure=Decimal("100000"),
            max_portfolio_exposure=Decimal("500000"),
            max_concurrent_trades=10,
            max_leverage=Decimal("5"),
            max_slippage_bps=Decimal("25"),
            max_data_age_seconds=30,
            max_order_notional=Decimal("100000"),
            min_risk_reward=Decimal("1"),
        )
    )


@pytest.mark.asyncio
async def test_market_data_to_paper_order_vertical_slice():
    instrument = Instrument("NSE_EQ|TEST", "NSE", "TEST", "EQUITY")
    adapter = FakePaperAdapter()
    pipeline = QuoteIngestionPipeline(adapter)
    quality = QuoteQualityGate(max_age=timedelta(minutes=2))
    candles = CandleEngine(interval_seconds=60)
    emitted = []
    now = datetime(2026, 1, 2, 9, 16, 1, tzinfo=timezone.utc)

    async for event in pipeline.stream([instrument]):
        observation = quality.evaluate(event, now=now)
        assert observation.accepted
        completed = candles.update(event)
        if completed is not None:
            emitted.append(completed)

    assert len(emitted) == 1
    assert emitted[0].open == Decimal("100")
    assert emitted[0].close == Decimal("101")
    assert emitted[0].volume == 10

    workflow = PaperExecutionWorkflow(risk_engine())
    context = RiskContext(
        now=now,
        market_open=True,
        last_market_data_at=now,
        snapshot=RiskSnapshot(available_liquidity=Decimal("100000")),
        order_notional=Decimal("100"),
        market_status=MarketStatus("NSE", "NORMAL_OPEN", now),
        expected_exchange="NSE",
    )
    order = OmsOrder("paper-smoke-1", instrument.instrument, 1)
    result = workflow.submit(order, Opportunity(), context, client_key="paper-smoke-1")
    assert result.risk.allowed
    assert result.order.state is OmsState.SCANNED
    await pipeline.close()
    assert adapter.closed
