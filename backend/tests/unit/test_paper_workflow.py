from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal

from advance_system.domain.market_status import MarketStatus
from advance_system.execution.paper_workflow import PaperExecutionWorkflow
from advance_system.oms.state_machine import OmsOrder, OmsState
from advance_system.risk.engine import RiskContext, RiskEngine, RiskPolicy, RiskSnapshot


class Opportunity:
    risk_reward = Decimal("2")


def context() -> RiskContext:
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
    return RiskContext(
        now=now,
        market_open=True,
        last_market_data_at=now,
        snapshot=RiskSnapshot(available_liquidity=Decimal("100000")),
        order_notional=Decimal("100"),
        market_status=MarketStatus("NSE", "NORMAL_OPEN", now),
        expected_exchange="NSE",
    )


def engine() -> RiskEngine:
    return RiskEngine(RiskPolicy(
        max_daily_loss=Decimal("100000"), max_strategy_loss=Decimal("50000"),
        max_symbol_exposure=Decimal("100000"), max_portfolio_exposure=Decimal("500000"),
        max_concurrent_trades=10, max_leverage=Decimal("5"),
        max_slippage_bps=Decimal("25"), max_data_age_seconds=30,
        min_risk_reward=Decimal("1"),
    ))


def test_workflow_rejects_before_oms_when_risk_fails() -> None:
    workflow = PaperExecutionWorkflow(engine())
    order = OmsOrder("paper-1", "NSE_EQ|TEST", 10)
    result = workflow.submit(order, Opportunity(), replace(context(), market_open=False), client_key="opp-1")
    assert result.risk.allowed is False
    assert result.order.state is OmsState.SCANNED


def test_approved_order_enters_paper_oms_and_is_idempotent() -> None:
    workflow = PaperExecutionWorkflow(engine())
    order = OmsOrder("paper-2", "NSE_EQ|TEST", 10)
    result = workflow.submit(order, Opportunity(), context(), client_key="opp-2")
    assert result.risk.allowed
    assert result.order.order_id == order.order_id
    assert result.replayed is False
    replay = workflow.submit(order, Opportunity(), context(), client_key="opp-2")
    assert replay.replayed is True
