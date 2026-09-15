from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from math import erf, exp, isfinite, log, pi, sqrt

from advance_system.market.derivatives import OptionType


@dataclass(frozen=True, slots=True)
class OptionAnalyticsInput:
    spot: Decimal
    strike: Decimal
    time_to_expiry_years: Decimal
    risk_free_rate: Decimal
    volatility: Decimal
    dividend_yield: Decimal = Decimal("0")
    option_type: OptionType = OptionType.CALL

    def validate(self) -> None:
        values = (self.spot, self.strike, self.time_to_expiry_years, self.risk_free_rate, self.volatility, self.dividend_yield)
        if not all(isfinite(float(value)) for value in values):
            raise ValueError("option inputs must be finite")
        if self.spot <= 0 or self.strike <= 0:
            raise ValueError("spot and strike must be positive")
        if self.time_to_expiry_years <= 0:
            raise ValueError("time to expiry must be positive")
        if self.volatility <= 0:
            raise ValueError("volatility must be positive")


@dataclass(frozen=True, slots=True)
class OptionGreeks:
    price: Decimal
    delta: Decimal
    gamma: Decimal
    vega: Decimal
    theta_per_day: Decimal
    rho: Decimal


def black_scholes_greeks(inputs: OptionAnalyticsInput) -> OptionGreeks:
    """Calculate European option price and standard Black-Scholes Greeks."""
    inputs.validate()
    s, k, t = map(float, (inputs.spot, inputs.strike, inputs.time_to_expiry_years))
    r, sigma, q = map(float, (inputs.risk_free_rate, inputs.volatility, inputs.dividend_yield))
    root_t = sqrt(t)
    d1 = (log(s / k) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * root_t)
    d2 = d1 - sigma * root_t
    nd1 = _normal_pdf(d1)
    n1, n2 = _normal_cdf(d1), _normal_cdf(d2)
    dr, dq = exp(-r * t), exp(-q * t)

    if inputs.option_type == OptionType.CALL:
        price = s * dq * n1 - k * dr * n2
        delta = dq * n1
        rho = k * t * dr * n2 / 100
        theta = (-s * dq * nd1 * sigma / (2 * root_t) - r * k * dr * n2 + q * s * dq * n1) / 365
    else:
        price = k * dr * _normal_cdf(-d2) - s * dq * _normal_cdf(-d1)
        delta = dq * (n1 - 1)
        rho = -k * t * dr * _normal_cdf(-d2) / 100
        theta = (-s * dq * nd1 * sigma / (2 * root_t) + r * k * dr * _normal_cdf(-d2) - q * s * dq * _normal_cdf(-d1)) / 365

    gamma = dq * nd1 / (s * sigma * root_t)
    vega = s * dq * nd1 * root_t / 100
    return OptionGreeks(*(_decimal(v) for v in (price, delta, gamma, vega, theta, rho)))


def implied_volatility(
    *,
    market_price: Decimal,
    inputs: OptionAnalyticsInput,
    tolerance: Decimal = Decimal("0.0000001"),
    max_iterations: int = 200,
) -> Decimal:
    """Solve European implied volatility with a deterministic bounded bisection solver."""
    if market_price <= 0:
        raise ValueError("market price must be positive")
    if tolerance <= 0 or max_iterations <= 0:
        raise ValueError("invalid IV solver configuration")
    inputs.validate()
    intrinsic = _intrinsic(inputs)
    target = float(market_price)
    if target + float(tolerance) < intrinsic:
        raise ValueError("market price is below intrinsic value")

    low, high = 1e-8, 8.0
    low_price = _price_at_vol(inputs, low)
    high_price = _price_at_vol(inputs, high)
    if target < low_price - float(tolerance) or target > high_price + float(tolerance):
        raise ValueError("market price is outside the supported volatility range")

    for _ in range(max_iterations):
        mid = (low + high) / 2
        price = _price_at_vol(inputs, mid)
        if abs(price - target) <= float(tolerance):
            return _decimal(mid)
        if price < target:
            low = mid
        else:
            high = mid
    raise ValueError("implied volatility did not converge")


@dataclass(frozen=True, slots=True)
class FuturesBasis:
    spot: Decimal
    futures: Decimal
    absolute: Decimal
    percentage: Decimal


def futures_basis(*, spot: Decimal, futures: Decimal) -> FuturesBasis:
    if spot <= 0 or futures <= 0:
        raise ValueError("spot and futures prices must be positive")
    absolute = futures - spot
    return FuturesBasis(spot=spot, futures=futures, absolute=absolute, percentage=absolute / spot)


def _price_at_vol(inputs: OptionAnalyticsInput, volatility: float) -> float:
    probe = OptionAnalyticsInput(
        spot=inputs.spot,
        strike=inputs.strike,
        time_to_expiry_years=inputs.time_to_expiry_years,
        risk_free_rate=inputs.risk_free_rate,
        volatility=Decimal(str(volatility)),
        dividend_yield=inputs.dividend_yield,
        option_type=inputs.option_type,
    )
    return float(black_scholes_greeks(probe).price)


def _intrinsic(inputs: OptionAnalyticsInput) -> float:
    s, k = float(inputs.spot), float(inputs.strike)
    return max(s - k, 0.0) if inputs.option_type == OptionType.CALL else max(k - s, 0.0)


def _normal_pdf(value: float) -> float:
    return exp(-0.5 * value * value) / sqrt(2 * pi)


def _normal_cdf(value: float) -> float:
    return 0.5 * (1 + erf(value / sqrt(2)))


def _decimal(value: float) -> Decimal:
    return Decimal(str(round(value, 12)))
