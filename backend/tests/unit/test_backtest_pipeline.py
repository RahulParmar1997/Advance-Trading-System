from datetime import datetime, timezone
from decimal import Decimal

from advance_system.backtest.engine import BacktestEvent
from advance_system.backtest.pipeline import IntegratedBacktestPipeline
from advance_system.oms.state_machine import OmsState
from advance_system.risk.engine import RiskEngine, RiskPolicy
from advance_system.strategy.engine import BreakoutContinuationV1


def permissive_risk() -> RiskEngine:
    return RiskEngine(
        RiskPolicy(
            max_daily_loss=Decimal("100000"),
            max_strategy_loss=Decimal("100000"),
            max_symbol_exposure=Decimal("100000"),
            max_portfolio_exposure=Decimal("100000"),
            max_concurrent_trades=10,
            max_leverage=Decimal("10"),
            max_slippage_bps=Decimal("100"),
            max_data_age_seconds=60,
            min_risk_reward=Decimal("1"),
            min_probability=Decimal("0"),
            max_order_notional=Decimal("100000"),
            max_participation_rate=Decimal("1"),
        )
    )


def test_integrated_pipeline_reaches_order_pending_without_lookahead() -> None:
    ts = datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc)
    events = [BacktestEvent(ts, "NSE_EQ|TEST", Decimal("100"))]
    result = IntegratedBacktestPipeline(BreakoutContinuationV1(), permissive_risk()).run(
        events,
        trade_type="BREAKOUT",
        stop=Decimal("95"),
        target=Decimal("110"),
        quantity=10,
        starting_cash=Decimal("10000"),
        probability=Decimal("0.6"),
        market_context={"structure_direction": "UP"},
    )
    assert result.decisions[0].risk_allowed is True
    assert result.decisions[0].oms_state is OmsState.ORDER_PENDING
    assert result.fills[0].price == Decimal("100")


def test_risk_rejection_never_reaches_execution() -> None:
    ts = datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc)
    result = IntegratedBacktestPipeline(BreakoutContinuationV1(), permissive_risk()).run(
        [BacktestEvent(ts, "NSE_EQ|TEST", Decimal("100"))],
        trade_type="BREAKOUT",
        stop=Decimal("99"),
        target=Decimal("101"),
        quantity=2000,
        starting_cash=Decimal("10000"),
        market_context={"structure_direction": "UP"},
    )
    assert result.decisions[0].risk_allowed is False
    assert result.decisions[0].oms_state is OmsState.REJECTED
    assert result.fills == ()


def test_strategy_rejection_does_not_create_opportunity() -> None:
    ts = datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc)
    result = IntegratedBacktestPipeline(BreakoutContinuationV1(), permissive_risk()).run(
        [BacktestEvent(ts, "NSE_EQ|TEST", Decimal("100"))],
        trade_type="MEAN_REVERSION",
        stop=Decimal("95"),
        target=Decimal("110"),
        quantity=10,
        starting_cash=Decimal("10000"),
    )
    assert result.decisions[0].opportunity is None
    assert result.decisions[0].oms_state is OmsState.REJECTED
