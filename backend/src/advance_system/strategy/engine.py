from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


@dataclass(frozen=True, slots=True)
class StrategyContext:
    instrument: str
    trade_type: str
    market_context: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class StrategyDecision:
    strategy: str
    version: str
    eligible: bool
    direction: str | None
    reason: str


class Strategy(Protocol):
    name: str
    version: str

    def evaluate(self, context: StrategyContext) -> StrategyDecision:
        ...


class StrategyRegistry:
    """Versioned strategy registry; strategies never submit orders."""

    def __init__(self) -> None:
        self._strategies: dict[tuple[str, str], Strategy] = {}

    def register(self, strategy: Strategy) -> None:
        key = (strategy.name, strategy.version)
        if key in self._strategies:
            raise ValueError(f"strategy already registered: {strategy.name}@{strategy.version}")
        self._strategies[key] = strategy

    def get(self, name: str, version: str) -> Strategy:
        return self._strategies[(name, version)]


class BreakoutContinuationV1:
    name = "breakout-continuation"
    version = "1.0.0"

    def evaluate(self, context: StrategyContext) -> StrategyDecision:
        if context.trade_type != "BREAKOUT":
            return StrategyDecision(self.name, self.version, False, None, "trade type mismatch")
        direction = context.market_context.get("structure_direction")
        if direction not in {"UP", "DOWN"}:
            return StrategyDecision(self.name, self.version, False, None, "structure direction unavailable")
        return StrategyDecision(self.name, self.version, True, str(direction), "breakout structure confirmed")
