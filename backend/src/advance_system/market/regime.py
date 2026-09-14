from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from statistics import mean
from typing import Sequence

from advance_system.market.candle_engine import Candle
from advance_system.market.structure import SwingPoint, SwingType


class MarketRegime(StrEnum):
    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    RANGE = "RANGE"
    TRANSITION = "TRANSITION"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(frozen=True, slots=True)
class RegimeObservation:
    instrument: str
    regime: MarketRegime
    confidence: Decimal
    volatility: Decimal
    trend_strength: Decimal
    range_width: Decimal
    evidence: tuple[str, ...]


class MarketRegimeEngine:
    """Deterministic regime classifier; it describes conditions, not signals."""

    def __init__(self, *, minimum_candles: int = 20, range_threshold: Decimal = Decimal("0.015")) -> None:
        if minimum_candles < 2:
            raise ValueError("minimum_candles must be at least 2")
        if range_threshold <= 0:
            raise ValueError("range_threshold must be positive")
        self.minimum_candles = minimum_candles
        self.range_threshold = range_threshold

    def classify(self, candles: Sequence[Candle], swings: Sequence[SwingPoint] = ()) -> RegimeObservation:
        if not candles:
            raise ValueError("candles cannot be empty")
        instrument = candles[0].instrument
        if any(c.instrument != instrument for c in candles):
            raise ValueError("candles must contain one instrument")
        if len(candles) < self.minimum_candles:
            return RegimeObservation(instrument, MarketRegime.INSUFFICIENT_DATA, Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"), ("insufficient candles",))

        closes = [c.close for c in candles]
        returns = [abs(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes)) if closes[i - 1] > 0]
        volatility = Decimal(str(mean(returns))) if returns else Decimal("0")
        first, last = closes[0], closes[-1]
        trend_strength = abs(last - first) / first if first > 0 else Decimal("0")
        high = max(c.high for c in candles)
        low = min(c.low for c in candles)
        range_width = (high - low) / low if low > 0 else Decimal("0")

        high_points = [s.price for s in swings if s.kind is SwingType.HIGH]
        low_points = [s.price for s in swings if s.kind is SwingType.LOW]
        up_structure = len(high_points) >= 2 and high_points[-1] > high_points[-2] and len(low_points) >= 2 and low_points[-1] > low_points[-2]
        down_structure = len(high_points) >= 2 and high_points[-1] < high_points[-2] and len(low_points) >= 2 and low_points[-1] < low_points[-2]

        evidence: list[str] = []
        if up_structure:
            evidence.append("higher-high/higher-low structure")
        if down_structure:
            evidence.append("lower-high/lower-low structure")
        if range_width <= self.range_threshold:
            evidence.append("compressed price range")

        if up_structure and trend_strength > volatility:
            regime = MarketRegime.TREND_UP
        elif down_structure and trend_strength > volatility:
            regime = MarketRegime.TREND_DOWN
        elif range_width <= self.range_threshold:
            regime = MarketRegime.RANGE
        else:
            regime = MarketRegime.TRANSITION

        confidence = min(Decimal("1"), max(Decimal("0"), trend_strength / (volatility + Decimal("0.000001"))))
        if regime is MarketRegime.RANGE:
            confidence = min(Decimal("1"), max(Decimal("0"), self.range_threshold / (range_width + Decimal("0.000001"))))
        elif regime is MarketRegime.TRANSITION:
            confidence = Decimal("0.5")
        return RegimeObservation(instrument, regime, confidence, volatility, trend_strength, range_width, tuple(evidence))
