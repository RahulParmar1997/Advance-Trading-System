from datetime import datetime, timezone
from decimal import Decimal

from advance_system.backtest.engine import BacktestEvent
from advance_system.backtest.pipeline import IntegratedBacktestPipeline
from advance_system.domain.market_status import MarketStatus
from advance_system.risk.engine import RiskEngine, RiskPolicy
from advance_system.strategy.engine import BreakoutContinuationV1


def make_risk() -> RiskEngine:
    return RiskEngine(RiskPolicy(
        max_concurrent_trades=10,
        max_data_age_seconds=60,
        max_leverage=Decimal("10"),
        max_symbol_exposure=Decimal("100000"),
        max_portfolio_exposure=Decimal("100000"),
        max_order_notional=Decimal("100000"),
        max_slippage_bps=Decimal("100"),
        max_daily_loss=Decimal("100000"),
        max_strategy_loss=Decimal("100000"),
        max_participation_rate=Decimal("0"),
        min_risk_reward=Decimal("1"),
    ))


def test_integrated_pipeline_reaches_oms_pending_only_after_risk() -> None:
    event = BacktestEvent(datetime(2026, 1, 1, tzinfo=timezone.utc), "NSE_EQ|TEST", Decimal("100"))
    result = IntegratedBacktestPipeline(BreakoutContinuationV1(), make_risk()).run(
        [event],
        trade_type="BREAKOUT",
        stop=Decimal("95"),
        target=Decimal("110"),
        quantity=5,
        starting_cash=Decimal("10000"),
        market_context={"structure_direction": "UP"},
        market_status=MarketStatus("NSE", "NORMAL_OPEN", event.timestamp),
    )
    assert result.decisions[0].risk_allowed is True
    assert result.decisions[0].oms_state.value == "ORDER_PENDING"
    assert result.fills[0].quantity == 5


def test_integrated_pipeline_rejects_before_oms_when_risk_fails() -> None:
    event = BacktestEvent(datetime(2026, 1, 1, tzinfo=timezone.utc), "NSE_EQ|TEST", Decimal("100"))
    risk = RiskEngine(RiskPolicy(max_concurrent_trades=0, max_data_age_seconds=60))
    result = IntegratedBacktestPipeline(BreakoutContinuationV1(), risk).run(
        [event],
        trade_type="BREAKOUT",
        stop=Decimal("95"),
        target=Decimal("110"),
        quantity=5,
        starting_cash=Decimal("10000"),
        market_context={"structure_direction": "UP"},
        market_status=MarketStatus("NSE", "NORMAL_OPEN", event.timestamp),
    )
    assert result.decisions[0].risk_allowed is False
    assert result.decisions[0].oms_state.value == "REJECTED"
    assert result.fills == ()
