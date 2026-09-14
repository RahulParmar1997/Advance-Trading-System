from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class TradeType(StrEnum):
    TREND_CONTINUATION = "TREND_CONTINUATION"
    BREAKOUT = "BREAKOUT"
    MEAN_REVERSION = "MEAN_REVERSION"
    LIQUIDITY_SWEEP = "LIQUIDITY_SWEEP"
    REVERSAL = "REVERSAL"
    RANGE = "RANGE"


@dataclass(frozen=True, slots=True)
class TradeTypeDefinition:
    trade_type: TradeType
    enabled: bool = True
    required_context: tuple[str, ...] = ()

    def qualifies(self, context: Mapping[str, object]) -> bool:
        if not self.enabled:
            return False
        return all(key in context for key in self.required_context)


class TradeTypeRegistry:
    """Explicit WHAT layer; strategy logic remains separate."""

    def __init__(self, definitions: tuple[TradeTypeDefinition, ...] = ()) -> None:
        self._definitions = {definition.trade_type: definition for definition in definitions}

    def register(self, definition: TradeTypeDefinition) -> None:
        if definition.trade_type in self._definitions:
            raise ValueError(f"trade type already registered: {definition.trade_type}")
        self._definitions[definition.trade_type] = definition

    def get(self, trade_type: TradeType) -> TradeTypeDefinition:
        return self._definitions[trade_type]

    def qualify(self, context: Mapping[str, object]) -> tuple[TradeType, ...]:
        return tuple(
            trade_type
            for trade_type, definition in self._definitions.items()
            if definition.qualifies(context)
        )
