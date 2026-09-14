from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RiskContext:
    strategy_enabled: bool
    trade_type_enabled: bool
    market_open: bool
    data_fresh: bool
    duplicate_signal: bool
    daily_loss: Decimal
    max_daily_loss: Decimal


@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    reason: str


class RiskEngine:
    """Central hard gate between opportunity generation and OMS."""

    def evaluate(self, context: RiskContext) -> RiskDecision:
        if not context.strategy_enabled:
            return RiskDecision(False, "strategy_disabled")
        if not context.trade_type_enabled:
            return RiskDecision(False, "trade_type_disabled")
        if not context.market_open:
            return RiskDecision(False, "market_closed")
        if not context.data_fresh:
            return RiskDecision(False, "data_stale")
        if context.duplicate_signal:
            return RiskDecision(False, "duplicate_signal")
        if context.daily_loss >= context.max_daily_loss:
            return RiskDecision(False, "daily_loss_limit")
        return RiskDecision(True, "approved")
