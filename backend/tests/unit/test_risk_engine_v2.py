from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest

from advance_system.risk.engine import RiskContext, RiskEngine, RiskPolicy, RiskSnapshot


def context(**overrides):
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
    values = dict(
        now=now,
        market_open=True,
        last_market_data_at=now - timedelta(seconds=1),
        snapshot=RiskSnapshot(),
        strategy_valid=True,
        trade_type_enabled=True,
        duplicate_opportunity=False,
        estimated_slippage_bps=Decimal("1"),
        probability=Decimal("0.60"),
    )
    values.update(overrides)
    return RiskContext(**values)


def engine():
    return RiskEngine(
        RiskPolicy(
            max_daily_loss=Decimal("1000"),
            max_strategy_loss=Decimal("500"),
            max_symbol_exposure=Decimal("10000"),
            max_portfolio_exposure=Decimal("50000"),
            max_concurrent_trades=5,
            max_leverage=Decimal("3"),
            max_slippage_bps=Decimal("10"),
            max_data_age_seconds=5,
            min_risk_reward=Decimal("1.5"),
            min_probability=Decimal("0.55"),
        )
    )


def opportunity(rr="2"):
    return SimpleNamespace(risk_reward=Decimal(rr))


def test_all_hard_gates_pass():
    decision = engine().check(opportunity(), context())
    assert decision.allowed is True
    assert decision.reason == "all risk checks passed"


@pytest.mark.parametrize(
    "override,reason",
    [
        ({"market_open": False}, "market is closed"),
        ({"strategy_valid": False}, "strategy is invalid"),
        ({"trade_type_enabled": False}, "trade type is disabled"),
        ({"duplicate_opportunity": True}, "duplicate opportunity"),
        ({"estimated_slippage_bps": Decimal("11")}, "estimated slippage exceeds limit"),
        ({"probability": Decimal("0.50")}, "probability below minimum"),
    ],
)
def test_decision_specific_gates(override, reason):
    decision = engine().check(opportunity(), context(**override))
    assert decision.allowed is False
    assert decision.reason == reason


def test_stale_data_is_rejected():
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
    decision = engine().check(
        opportunity(),
        context(now=now, last_market_data_at=now - timedelta(seconds=6)),
    )
    assert decision.reason == "market data is stale"


def test_kill_switch_and_circuit_breaker_are_hard_stops():
    for snapshot in (RiskSnapshot(kill_switch=True), RiskSnapshot(circuit_breaker=True)):
        decision = engine().check(opportunity(), context(snapshot=snapshot))
        assert decision.allowed is False


def test_account_limits_are_enforced():
    snapshot = RiskSnapshot(symbol_exposure=Decimal("10001"))
    decision = engine().check(opportunity(), context(snapshot=snapshot))
    assert decision.reason == "symbol exposure limit exceeded"


def test_risk_reward_limit_is_enforced():
    decision = engine().check(opportunity("1.4"), context())
    assert decision.reason == "risk/reward below minimum"


def test_policy_rejects_invalid_probability():
    with pytest.raises(ValueError):
        RiskPolicy(min_probability=Decimal("1.1")).validate()
