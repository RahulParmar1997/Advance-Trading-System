from decimal import Decimal

import pytest

from advance_system.backtest.sensitivity import BacktestSensitivity


def test_monte_carlo_is_deterministic_with_seed() -> None:
    engine = BacktestSensitivity()
    a = engine.monte_carlo_resample([Decimal("10"), Decimal("-5")], simulations=50, seed=7)
    b = engine.monte_carlo_resample([Decimal("10"), Decimal("-5")], simulations=50, seed=7)
    assert a == b
    assert a.simulations == 50


def test_monte_carlo_reports_loss_probability() -> None:
    result = BacktestSensitivity().monte_carlo_resample([Decimal("-1")], simulations=10, seed=1)
    assert result.loss_probability == Decimal("1")
    assert result.worst_total_pnl == Decimal("-1")


def test_cost_sensitivity_increases_cost_with_fees() -> None:
    result = BacktestSensitivity().cost_sensitivity(
        [Decimal("100"), Decimal("50")],
        [Decimal("10000"), Decimal("5000")],
        [Decimal("0"), Decimal("10")],
    )
    assert result[0].total_pnl == Decimal("150")
    assert result[1].total_pnl == Decimal("135")


def test_capacity_sensitivity_rejects_over_participation() -> None:
    result = BacktestSensitivity().capacity_sensitivity(
        [Decimal("100"), Decimal("50")],
        [Decimal("100"), Decimal("300")],
        [Decimal("0.5")],
        [Decimal("300"), Decimal("400")],
    )
    assert result[0].total_pnl == Decimal("100")


def test_invalid_monte_carlo_inputs_are_rejected() -> None:
    with pytest.raises(ValueError):
        BacktestSensitivity().monte_carlo_resample([], simulations=10)
    with pytest.raises(ValueError):
        BacktestSensitivity().monte_carlo_resample([Decimal("1")], simulations=0)
