from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from advance_system.market.candle_engine import Candle
from advance_system.market.liquidity import FairValueGap, LiquidityLevel, LiquidityDetector, OrderBlock
from advance_system.market.structure import MarketStructureEngine, StructureSignal, SwingDetector, SwingPoint


@dataclass(frozen=True, slots=True)
class MarketState:
    instrument: str
    timeframe_seconds: int
    candles: tuple[Candle, ...]
    swings: tuple[SwingPoint, ...]
    structure_signals: tuple[StructureSignal, ...]
    liquidity_levels: tuple[LiquidityLevel, ...]
    fair_value_gaps: tuple[FairValueGap, ...]
    order_blocks: tuple[OrderBlock, ...]


class MarketStateEngine:
    """Pure composition layer for deterministic market-state observations."""

    def __init__(self, *, swing_left: int = 2, swing_right: int = 2) -> None:
        self.swings = SwingDetector(left=swing_left, right=swing_right)
        self.structure = MarketStructureEngine()
        self.liquidity = LiquidityDetector()

    def build(self, candles: Sequence[Candle], *, timeframe_seconds: int) -> MarketState:
        if timeframe_seconds <= 0:
            raise ValueError("timeframe_seconds must be positive")
        if not candles:
            raise ValueError("candles cannot be empty")
        instruments = {c.instrument for c in candles}
        if len(instruments) != 1:
            raise ValueError("MarketState requires one instrument")
        swings = self.swings.detect(candles)
        return MarketState(
            instrument=candles[0].instrument,
            timeframe_seconds=timeframe_seconds,
            candles=tuple(candles),
            swings=tuple(swings),
            structure_signals=tuple(self.structure.signals(candles, swings)),
            liquidity_levels=tuple(self.liquidity.equal_highs(candles) + self.liquidity.equal_lows(candles)),
            fair_value_gaps=tuple(self.liquidity.fair_value_gaps(candles)),
            order_blocks=tuple(self.liquidity.order_blocks(candles)),
        )
