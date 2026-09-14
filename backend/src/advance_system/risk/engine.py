from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from advance_system.domain.market_status import MarketStatus


@dataclass(frozen=True, slots=True)
class RiskPolicy:
    """Conservative pre-trade limits. Values are explicit, never inferred."""

    max_daily_loss: Decimal = Decimal("0")
    max_strategy_loss: Decimal = Decimal("0")
    max_symbol_exposure: Decimal = Decimal("0")
    max_portfolio_exposure: Decimal = Decimal("0")
    max_concurrent_trades: int = 0
    max_leverage: Decimal = Decimal("0")
    max_slippage_bps: Decimal = Decimal("0")
    max_data_age_seconds: int = 0
    max_market_status_age_seconds: int = 60
    min_risk_reward: Decimal = Decimal("0")
    min_probability: Decimal = Decimal("0")
    max_order_notional: Decimal = Decimal("0")
    max_participation_rate: Decimal = Decimal("0")
    require_authoritative_market_status: bool = True

    def validate(self) -> None:
        if self.max_daily_loss < 0 or self.max_strategy_loss < 0:
            raise ValueError("loss limits cannot be negative")
        if self.max_symbol_exposure < 0 or self.max_portfolio_exposure < 0 or self.max_order_notional < 0:
            raise ValueError("exposure limits cannot be negative")
        if self.max_concurrent_trades < 0 or self.max_data_age_seconds < 0 or self.max_market_status_age_seconds < 0:
            raise ValueError("count and age limits cannot be negative")
        if self.max_leverage < 0 or self.max_slippage_bps < 0:
            raise ValueError("leverage and slippage limits cannot be negative")
        if self.min_risk_reward < 0:
            raise ValueError("minimum risk/reward cannot be negative")
        if not Decimal("0") <= self.min_probability <= Decimal("1"):
            raise ValueError("minimum probability must be between 0 and 1")
        if not Decimal("0") <= self.max_participation_rate <= Decimal("1"):
            raise ValueError("participation rate must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class RiskSnapshot:
    daily_pnl: Decimal = Decimal("0")
    strategy_pnl: Decimal = Decimal("0")
    symbol_exposure: Decimal = Decimal("0")
    portfolio_exposure: Decimal = Decimal("0")
    concurrent_trades: int = 0
    leverage: Decimal = Decimal("0")
    broker_healthy: bool = True
    kill_switch: bool = False
    circuit_breaker: bool = False
    available_liquidity: Decimal = Decimal("0")


@dataclass(frozen=True, slots=True)
class RiskContext:
    now: datetime
    market_open: bool
    last_market_data_at: datetime
    snapshot: RiskSnapshot
    strategy_valid: bool = True
    trade_type_enabled: bool = True
    duplicate_opportunity: bool = False
    estimated_slippage_bps: Decimal = Decimal("0")
    probability: Decimal | None = None
    order_notional: Decimal = Decimal("0")
    estimated_market_volume: Decimal = Decimal("0")
    market_status: MarketStatus | None = None
    expected_exchange: str | None = None


@dataclass(frozen=True, slots=True)
class RiskDecision:
    allowed: bool
    reason: str
    checks: tuple[str, ...] = ()


class RiskEngine:
    """Hard pre-trade gate. No order may proceed unless every check passes."""

    def __init__(self, policy: RiskPolicy | None = None) -> None:
        self.policy = policy or RiskPolicy()
        self.policy.validate()

    def check(self, opportunity: object, context: RiskContext) -> RiskDecision:
        checks: list[str] = []
        policy = self.policy
        snapshot = context.snapshot

        if context.now.tzinfo is None or context.last_market_data_at.tzinfo is None:
            return RiskDecision(False, "timestamps must be timezone-aware", tuple(checks))
        if context.last_market_data_at > context.now:
            return RiskDecision(False, "market data timestamp is in the future", tuple(checks))
        if (context.now - context.last_market_data_at) > timedelta(seconds=policy.max_data_age_seconds):
            return RiskDecision(False, "market data is stale", tuple(checks))
        checks.append("data freshness")

        if not context.market_open:
            return RiskDecision(False, "market is closed", tuple(checks))
        if policy.require_authoritative_market_status:
            if context.market_status is None:
                return RiskDecision(False, "authoritative market status unavailable", tuple(checks))
            try:
                context.market_status.validate()
            except ValueError:
                return RiskDecision(False, "authoritative market status is invalid", tuple(checks))
            status_at = context.market_status.observed_at.astimezone(timezone.utc)
            now = context.now.astimezone(timezone.utc)
            if status_at > now:
                return RiskDecision(False, "market status timestamp is in the future", tuple(checks))
            if now - status_at > timedelta(seconds=policy.max_market_status_age_seconds):
                return RiskDecision(False, "market status is stale", tuple(checks))
            if context.expected_exchange and context.market_status.exchange.upper() != context.expected_exchange.strip().upper():
                return RiskDecision(False, "market status exchange mismatch", tuple(checks))
            if not context.market_status.is_normal_open:
                return RiskDecision(False, "market status is not normal open", tuple(checks))
            checks.append("authoritative market status")
        checks.append("market session")

        if snapshot.kill_switch:
            return RiskDecision(False, "kill switch active", tuple(checks))
        if snapshot.circuit_breaker:
            return RiskDecision(False, "circuit breaker active", tuple(checks))
        if not snapshot.broker_healthy:
            return RiskDecision(False, "broker is unhealthy", tuple(checks))
        checks.append("system safety")

        if not context.strategy_valid:
            return RiskDecision(False, "strategy is invalid", tuple(checks))
        if not context.trade_type_enabled:
            return RiskDecision(False, "trade type is disabled", tuple(checks))
        if context.duplicate_opportunity:
            return RiskDecision(False, "duplicate opportunity", tuple(checks))
        checks.append("decision validity")

        for name, value, limit in (
            ("daily loss", -snapshot.daily_pnl, policy.max_daily_loss),
            ("strategy loss", -snapshot.strategy_pnl, policy.max_strategy_loss),
            ("symbol exposure", snapshot.symbol_exposure, policy.max_symbol_exposure),
            ("portfolio exposure", snapshot.portfolio_exposure, policy.max_portfolio_exposure),
        ):
            if value > limit:
                return RiskDecision(False, f"{name} limit exceeded", tuple(checks))
        if snapshot.concurrent_trades >= policy.max_concurrent_trades:
            return RiskDecision(False, "concurrent trade limit exceeded", tuple(checks))
        if snapshot.leverage > policy.max_leverage:
            return RiskDecision(False, "leverage limit exceeded", tuple(checks))
        checks.append("account limits")

        if context.order_notional <= 0:
            return RiskDecision(False, "order notional must be positive", tuple(checks))
        if policy.max_order_notional and context.order_notional > policy.max_order_notional:
            return RiskDecision(False, "order notional limit exceeded", tuple(checks))
        if snapshot.available_liquidity < context.order_notional:
            return RiskDecision(False, "insufficient available liquidity", tuple(checks))
        if policy.max_participation_rate and context.estimated_market_volume <= 0:
            return RiskDecision(False, "market volume is unavailable for participation check", tuple(checks))
        if policy.max_participation_rate and context.order_notional > context.estimated_market_volume * policy.max_participation_rate:
            return RiskDecision(False, "market participation limit exceeded", tuple(checks))
        checks.append("capacity")

        rr = getattr(opportunity, "risk_reward", None)
        if rr is None or rr < policy.min_risk_reward:
            return RiskDecision(False, "risk/reward below minimum", tuple(checks))
        if context.estimated_slippage_bps > policy.max_slippage_bps:
            return RiskDecision(False, "estimated slippage exceeds limit", tuple(checks))
        if context.probability is not None and context.probability < policy.min_probability:
            return RiskDecision(False, "probability below minimum", tuple(checks))
        checks.append("opportunity quality")

        return RiskDecision(True, "all risk checks passed", tuple(checks))
