from decimal import Decimal

import pytest

from advance_system.market.derivative_analytics import (
    OptionAnalyticsInput,
    black_scholes_greeks,
    futures_basis,
    implied_volatility,
)
from advance_system.market.derivatives import OptionType


def inputs(option_type=OptionType.CALL, volatility=Decimal("0.20")):
    return OptionAnalyticsInput(
        spot=Decimal("100"),
        strike=Decimal("100"),
        time_to_expiry_years=Decimal("1"),
        risk_free_rate=Decimal("0.05"),
        volatility=volatility,
        option_type=option_type,
    )


def test_black_scholes_call_is_deterministic_and_valid():
    result = black_scholes_greeks(inputs())
    assert result.price == Decimal("10.450583572186")
    assert Decimal("0") < result.delta < Decimal("1")
    assert result.gamma > 0
    assert result.vega > 0
    assert result.theta_per_day < 0


def test_put_delta_is_negative():
    result = black_scholes_greeks(inputs(OptionType.PUT))
    assert result.delta < 0
    assert result.rho < 0


def test_implied_volatility_recovers_known_volatility():
    source = inputs(volatility=Decimal("0.30"))
    market_price = black_scholes_greeks(source).price
    recovered = implied_volatility(market_price=market_price, inputs=inputs(volatility=Decimal("0.20")))
    assert abs(recovered - Decimal("0.30")) < Decimal("0.000001")


def test_iv_rejects_price_below_intrinsic():
    with pytest.raises(ValueError, match="intrinsic"):
        implied_volatility(market_price=Decimal("1"), inputs=inputs())


def test_invalid_option_inputs_fail_closed():
    with pytest.raises(ValueError, match="positive"):
        black_scholes_greeks(OptionAnalyticsInput(Decimal("0"), Decimal("100"), Decimal("1"), Decimal("0.05"), Decimal("0.2")))


def test_futures_basis():
    result = futures_basis(spot=Decimal("100"), futures=Decimal("102.5"))
    assert result.absolute == Decimal("2.5")
    assert result.percentage == Decimal("0.025")


def test_futures_basis_rejects_non_positive_price():
    with pytest.raises(ValueError, match="positive"):
        futures_basis(spot=Decimal("0"), futures=Decimal("100"))
