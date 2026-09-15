from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from advance_system.market.candle_engine import Candle


@dataclass(frozen=True, slots=True)
class DisplacementConfig:
    """Explicit thresholds for classifying a completed candle as displacement."""

    min_body_to_range: Decimal = Decimal("0.70")
    min_range_to_average: Decimal = Decimal("1.50")
    lookback: int = 5

    def validate(self) -> None:
        if not Decimal("0") < self.min_body_to_range <= Decimal("1"):
            raise ValueError("min_body_to_range must be between 0 and 1")
        if self.min_range_to_average <= 0:
            raise ValueError("min_range_to_average must be positive")
        if self.lookback <= 0:
            raise ValueError("lookback must be positive")


@dataclass(frozen=True, slots=True)
class CandleFeatures:
    instrument: str
    close: Decimal
    range: Decimal
    body: Decimal
    direction: str
    volume: int
    body_to_range: Decimal = Decimal("0")
    average_prior_range: Decimal | None = None
    range_to_average: Decimal | None = None
    displacement: bool = False
    displacement_direction: str = "NONE"


class FeatureEngine:
    """Pure deterministic feature calculations over completed candles only."""

    def __init__(self, displacement: DisplacementConfig | None = None) -> None:
        self.displacement = displacement or DisplacementConfig()
        self.displacement.validate()

    def calculate(self, candle: Candle, previous_candles: Sequence[Candle] = ()) -> CandleFeatures:
        self._validate_candle(candle)
        candle_range = candle.high - candle.low
        body = abs(candle.close - candle.open)
        direction = "UP" if candle.close > candle.open else "DOWN" if candle.close < candle.open else "FLAT"
        body_to_range = body / candle_range if candle_range > 0 else Decimal("0")

        prior = self._prior_ranges(candle, previous_candles)
        average_prior_range = sum(prior, Decimal("0")) / Decimal(len(prior)) if prior else None
        range_to_average = candle_range / average_prior_range if average_prior_range and average_prior_range > 0 else None
        displacement = (
            candle_range > 0
            and body_to_range >= self.displacement.min_body_to_range
            and range_to_average is not None
            and range_to_average >= self.displacement.min_range_to_average
            and direction != "FLAT"
        )

        return CandleFeatures(
            instrument=candle.instrument,
            close=candle.close,
            range=candle_range,
            body=body,
            direction=direction,
            volume=candle.volume,
            body_to_range=body_to_range,
            average_prior_range=average_prior_range,
            range_to_average=range_to_average,
            displacement=displacement,
            displacement_direction=direction if displacement else "NONE",
        )

    def _prior_ranges(self, candle: Candle, previous_candles: Sequence[Candle]) -> tuple[Decimal, ...]:
        prior = tuple(previous_candles)
        if len(prior) > self.displacement.lookback:
            prior = prior[-self.displacement.lookback :]
        for previous in prior:
            self._validate_candle(previous)
            if previous.instrument != candle.instrument:
                raise ValueError("previous candles must use one instrument")
            if previous.end >= candle.end:
                raise ValueError("previous candles must precede the completed candle")
        return tuple(previous.high - previous.low for previous in prior)

    @staticmethod
    def _validate_candle(candle: Candle) -> None:
        if candle.end <= candle.start:
            raise ValueError("candle end must be after start")
        if candle.high < candle.low:
            raise ValueError("candle high cannot be below low")
        if candle.open < candle.low or candle.open > candle.high:
            raise ValueError("candle open must be within range")
        if candle.close < candle.low or candle.close > candle.high:
            raise ValueError("candle close must be within range")
        if candle.session_date is not None and candle.session_phase is None:
            raise ValueError("session-aware candle must include session phase")
        if candle.session_phase is not None and candle.session_date is None:
            raise ValueError("session-aware candle must include session date")
