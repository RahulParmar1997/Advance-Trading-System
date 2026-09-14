import pytest

from advance_system.strategy.engine import BreakoutContinuationV1, StrategyContext, StrategyRegistry


def test_breakout_strategy_requires_breakout_trade_type():
    strategy = BreakoutContinuationV1()
    rejected = strategy.evaluate(StrategyContext("NSE_EQ|TEST", "RANGE", {"structure_direction": "UP"}))
    assert not rejected.eligible


def test_breakout_strategy_is_deterministic_and_returns_direction():
    strategy = BreakoutContinuationV1()
    context = StrategyContext("NSE_EQ|TEST", "BREAKOUT", {"structure_direction": "UP"})
    first = strategy.evaluate(context)
    second = strategy.evaluate(context)
    assert first == second
    assert first.eligible
    assert first.direction == "UP"
    assert first.version == "1.0.0"


def test_registry_is_version_aware():
    registry = StrategyRegistry()
    strategy = BreakoutContinuationV1()
    registry.register(strategy)
    assert registry.get(strategy.name, strategy.version) is strategy
    with pytest.raises(ValueError):
        registry.register(BreakoutContinuationV1())
