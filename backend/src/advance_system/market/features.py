from dataclasses import dataclass
from decimal import Decimal

from advance_system.market.candle_engine import Candle


@dataclass(frozen=True, slots=True)
class CandleFeatures:
    instrument: str
    close: Decimal
    range: Decimal
    body: Decimal
    direction: str
    volume: int


class FeatureEngine:
    """Pure deterministic candle feature calculations."""

    def calculate(self, candle: Candle) -> CandleFeatures:
        candle_range = candle.high - candle.low
        return CandleFeatures(
            instrument=candle.instrument,
            close=candle.close,
            range=candle_range,
            body=abs(candle.close - candle.open),
            direction=(
                "UP" if candle.close > candle.open
                else "DOWN" if candle.close < candle.open
                else "FLAT"
            ),
            volume=candle.volume,
        )
