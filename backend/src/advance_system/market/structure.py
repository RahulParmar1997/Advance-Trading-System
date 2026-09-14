from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Sequence

from advance_system.market.candle_engine import Candle


class SwingType(StrEnum):
    HIGH = "SWING_HIGH"
    LOW = "SWING_LOW"


class StructureEvent(StrEnum):
    BOS = "BOS"
    CHOCH = "CHoCH"
    MSS = "MSS"


@dataclass(frozen=True, slots=True)
class SwingPoint:
    instrument: str
    timestamp: object
    price: Decimal
    kind: SwingType
    index: int


@dataclass(frozen=True, slots=True)
class StructureSignal:
    instrument: str
    timestamp: object
    event: StructureEvent
    direction: str
    broken_price: Decimal
    swing_index: int


class SwingDetector:
    """Deterministic confirmed swing detector.

    A swing is confirmed only after `left` candles on both sides exist. This
    intentionally avoids look-ahead in downstream backtests: the signal timestamp
    remains the confirmation candle timestamp, not the pivot candle timestamp.
    """

    def __init__(self, *, left: int = 2, right: int = 2) -> None:
        if left < 1 or right < 1:
            raise ValueError("left and right must be positive")
        self.left = left
        self.right = right

    def detect(self, candles: Sequence[Candle]) -> list[SwingPoint]:
        if len(candles) < self.left + self.right + 1:
            return []
        result: list[SwingPoint] = []
        start = self.left
        stop = len(candles) - self.right
        for i in range(start, stop):
            window = candles[i - self.left : i + self.right + 1]
            pivot = candles[i]
            highs = [c.high for c in window]
            lows = [c.low for c in window]
            if pivot.high == max(highs) and highs.count(pivot.high) == 1:
                result.append(SwingPoint(pivot.instrument, candles[i + self.right].end, pivot.high, SwingType.HIGH, i))
            if pivot.low == min(lows) and lows.count(pivot.low) == 1:
                result.append(SwingPoint(pivot.instrument, candles[i + self.right].end, pivot.low, SwingType.LOW, i))
        return result


class MarketStructureEngine:
    """Classifies HH/HL/LH/LL and emits deterministic BOS/CHoCH/MSS signals."""

    def classify_swings(self, swings: Sequence[SwingPoint]) -> list[str]:
        highs: list[Decimal] = []
        lows: list[Decimal] = []
        labels: list[str] = []
        for swing in swings:
            if swing.kind is SwingType.HIGH:
                label = "HH" if highs and swing.price > highs[-1] else "LH" if highs else "H"
                highs.append(swing.price)
            else:
                label = "HL" if lows and swing.price > lows[-1] else "LL" if lows else "L"
                lows.append(swing.price)
            labels.append(label)
        return labels

    def signals(self, candles: Sequence[Candle], swings: Sequence[SwingPoint]) -> list[StructureSignal]:
        if not swings or not candles:
            return []
        signals: list[StructureSignal] = []
        trend: str | None = None
        broken: set[int] = set()
        highs = [s for s in swings if s.kind is SwingType.HIGH]
        lows = [s for s in swings if s.kind is SwingType.LOW]
        for candle in candles:
            for swing in highs:
                if swing.index in broken or swing.timestamp >= candle.end:
                    continue
                if candle.close > swing.price:
                    event = StructureEvent.BOS if trend in (None, "UP") else StructureEvent.CHOCH
                    if trend == "DOWN":
                        event = StructureEvent.MSS
                    trend = "UP"
                    broken.add(swing.index)
                    signals.append(StructureSignal(candle.instrument, candle.end, event, "UP", swing.price, swing.index))
            for swing in lows:
                if swing.index in broken or swing.timestamp >= candle.end:
                    continue
                if candle.close < swing.price:
                    event = StructureEvent.BOS if trend in (None, "DOWN") else StructureEvent.CHOCH
                    if trend == "UP":
                        event = StructureEvent.MSS
                    trend = "DOWN"
                    broken.add(swing.index)
                    signals.append(StructureSignal(candle.instrument, candle.end, event, "DOWN", swing.price, swing.index))
        return signals
