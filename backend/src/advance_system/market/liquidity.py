from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Sequence

from advance_system.market.candle_engine import Candle


class LiquidityType(StrEnum):
    BUY_SIDE = "BUY_SIDE"
    SELL_SIDE = "SELL_SIDE"


@dataclass(frozen=True, slots=True)
class LiquidityLevel:
    instrument: str
    price: Decimal
    kind: LiquidityType
    source_index: int


@dataclass(frozen=True, slots=True)
class FairValueGap:
    instrument: str
    start: object
    end: object
    lower: Decimal
    upper: Decimal
    direction: str
    source_index: int


@dataclass(frozen=True, slots=True)
class OrderBlock:
    instrument: str
    timestamp: object
    lower: Decimal
    upper: Decimal
    direction: str
    source_index: int


class LiquidityDetector:
    """Deterministic liquidity/FVG/order-block primitives.

    These are descriptive market-structure observations, not trade guarantees.
    """

    def equal_highs(self, candles: Sequence[Candle], *, tolerance: Decimal = Decimal("0")) -> list[LiquidityLevel]:
        if tolerance < 0:
            raise ValueError("tolerance cannot be negative")
        result: list[LiquidityLevel] = []
        for i in range(1, len(candles)):
            if abs(candles[i].high - candles[i - 1].high) <= tolerance:
                result.append(LiquidityLevel(candles[i].instrument, candles[i].high, LiquidityType.BUY_SIDE, i))
        return result

    def equal_lows(self, candles: Sequence[Candle], *, tolerance: Decimal = Decimal("0")) -> list[LiquidityLevel]:
        if tolerance < 0:
            raise ValueError("tolerance cannot be negative")
        result: list[LiquidityLevel] = []
        for i in range(1, len(candles)):
            if abs(candles[i].low - candles[i - 1].low) <= tolerance:
                result.append(LiquidityLevel(candles[i].instrument, candles[i].low, LiquidityType.SELL_SIDE, i))
        return result

    def fair_value_gaps(self, candles: Sequence[Candle]) -> list[FairValueGap]:
        result: list[FairValueGap] = []
        for i in range(2, len(candles)):
            left, right = candles[i - 2], candles[i]
            if left.high < right.low:
                result.append(FairValueGap(right.instrument, left.end, right.end, left.high, right.low, "UP", i))
            elif left.low > right.high:
                result.append(FairValueGap(right.instrument, left.end, right.end, right.high, left.low, "DOWN", i))
        return result

    def order_blocks(self, candles: Sequence[Candle]) -> list[OrderBlock]:
        result: list[OrderBlock] = []
        for i in range(1, len(candles)):
            previous, current = candles[i - 1], candles[i]
            if current.close > current.open and previous.close < previous.open:
                result.append(OrderBlock(previous.instrument, previous.end, previous.low, previous.high, "UP", i - 1))
            elif current.close < current.open and previous.close > previous.open:
                result.append(OrderBlock(previous.instrument, previous.end, previous.low, previous.high, "DOWN", i - 1))
        return result
