from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Sequence

from advance_system.market.candle_engine import Candle


class WyckoffEvent(StrEnum):
    NONE = "NONE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    SPRING = "SPRING"
    UPTHRUST = "UPTHRUST"
    SIGN_OF_STRENGTH = "SIGN_OF_STRENGTH"
    SIGN_OF_WEAKNESS = "SIGN_OF_WEAKNESS"
    ABSORPTION = "ABSORPTION"


@dataclass(frozen=True, slots=True)
class WyckoffConfig:
    lookback: int = 5
    min_wide_spread_ratio: Decimal = Decimal("1.50")
    min_closing_location: Decimal = Decimal("0.75")
    min_volume_ratio: Decimal = Decimal("1.50")
    max_absorption_result_ratio: Decimal = Decimal("0.50")
    penetration_tolerance: Decimal = Decimal("0")

    def validate(self) -> None:
        if self.lookback <= 0:
            raise ValueError("lookback must be positive")
        if self.min_wide_spread_ratio <= 0:
            raise ValueError("min_wide_spread_ratio must be positive")
        if not Decimal("0") < self.min_closing_location <= Decimal("1"):
            raise ValueError("min_closing_location must be between 0 and 1")
        if self.min_volume_ratio <= 0:
            raise ValueError("min_volume_ratio must be positive")
        if not Decimal("0") < self.max_absorption_result_ratio <= Decimal("1"):
            raise ValueError("max_absorption_result_ratio must be between 0 and 1")
        if self.penetration_tolerance < 0:
            raise ValueError("penetration_tolerance cannot be negative")


@dataclass(frozen=True, slots=True)
class WyckoffFeatures:
    instrument: str
    observed_at: object
    spread: Decimal
    body: Decimal
    closing_location: Decimal
    prior_range_high: Decimal
    prior_range_low: Decimal
    average_prior_spread: Decimal
    average_prior_volume: Decimal
    volume_ratio: Decimal
    spread_ratio: Decimal
    effort_result_ratio: Decimal


@dataclass(frozen=True, slots=True)
class WyckoffObservation:
    instrument: str
    observed_at: object
    event: WyckoffEvent
    features: WyckoffFeatures | None
    evidence: tuple[str, ...] = ()


class WyckoffEngine:
    """Deterministic Wyckoff-style event features using completed candles only.

    Volume must be explicit candle volume. No tick/order-flow volume is inferred.
    Every comparison uses the current candle against strictly prior candles, so
    adding or changing future candles cannot change an already-built observation.
    """

    def __init__(self, config: WyckoffConfig | None = None) -> None:
        self.config = config or WyckoffConfig()
        self.config.validate()

    def observe(self, candles: Sequence[Candle]) -> WyckoffObservation:
        if not candles:
            raise ValueError("completed candles cannot be empty")
        self._validate_candles(candles)
        instrument = candles[0].instrument.strip()
        current = candles[-1]
        if len(candles) <= self.config.lookback:
            return WyckoffObservation(instrument, current.end, WyckoffEvent.INSUFFICIENT_DATA, None)

        prior = candles[-self.config.lookback - 1 : -1]
        average_spread = sum((c.high - c.low for c in prior), Decimal("0")) / Decimal(len(prior))
        average_volume = sum((Decimal(c.volume) for c in prior), Decimal("0")) / Decimal(len(prior))
        spread = current.high - current.low
        body = abs(current.close - current.open)
        if spread <= 0 or average_spread <= 0 or average_volume <= 0:
            raise ValueError("Wyckoff requires positive prior spread and volume")

        closing_location = (current.close - current.low) / spread
        volume_ratio = Decimal(current.volume) / average_volume
        spread_ratio = spread / average_spread
        effort_result_ratio = spread / Decimal(current.volume) if current.volume > 0 else Decimal("0")
        prior_high = max(c.high for c in prior)
        prior_low = min(c.low for c in prior)

        features = WyckoffFeatures(
            instrument=instrument,
            observed_at=current.end,
            spread=spread,
            body=body,
            closing_location=closing_location,
            prior_range_high=prior_high,
            prior_range_low=prior_low,
            average_prior_spread=average_spread,
            average_prior_volume=average_volume,
            volume_ratio=volume_ratio,
            spread_ratio=spread_ratio,
            effort_result_ratio=effort_result_ratio,
        )
        event, evidence = self._classify(current, features)
        return WyckoffObservation(instrument, current.end, event, features, tuple(evidence))

    def _classify(self, current: Candle, f: WyckoffFeatures) -> tuple[WyckoffEvent, list[str]]:
        cfg = self.config
        bullish_close = f.closing_location >= cfg.min_closing_location
        bearish_close = f.closing_location <= Decimal("1") - cfg.min_closing_location
        high_volume = f.volume_ratio >= cfg.min_volume_ratio
        wide = f.spread_ratio >= cfg.min_wide_spread_ratio
        tolerance = cfg.penetration_tolerance

        if current.low < f.prior_range_low - tolerance and current.close >= f.prior_range_low and high_volume:
            return WyckoffEvent.SPRING, ["prior support was pierced", "close reclaimed prior support", "volume was elevated"]
        if current.high > f.prior_range_high + tolerance and current.close <= f.prior_range_high and high_volume:
            return WyckoffEvent.UPTHRUST, ["prior resistance was pierced", "close returned below prior resistance", "volume was elevated"]
        if current.close > f.prior_range_high and current.close > current.open and wide and bullish_close and high_volume:
            return WyckoffEvent.SIGN_OF_STRENGTH, ["wide bullish spread", "close broke prior range high", "volume was elevated"]
        if current.close < f.prior_range_low and current.close < current.open and wide and bearish_close and high_volume:
            return WyckoffEvent.SIGN_OF_WEAKNESS, ["wide bearish spread", "close broke prior range low", "volume was elevated"]

        small_result = f.spread_ratio <= Decimal("1") and f.effort_result_ratio <= cfg.max_absorption_result_ratio / f.average_prior_volume
        if high_volume and small_result:
            return WyckoffEvent.ABSORPTION, ["volume was elevated", "spread was small relative to prior effort"]
        return WyckoffEvent.NONE, []

    @staticmethod
    def _validate_candles(candles: Sequence[Candle]) -> None:
        instrument = candles[0].instrument.strip()
        if not instrument:
            raise ValueError("candle instrument is required")
        for index, candle in enumerate(candles):
            if candle.instrument.strip() != instrument:
                raise ValueError("candles must contain one instrument")
            if candle.start.tzinfo is None or candle.end.tzinfo is None:
                raise ValueError("candle timestamps must be timezone-aware")
            if candle.end < candle.start:
                raise ValueError("candle end cannot precede start")
            if candle.high < candle.low or candle.high < candle.open or candle.high < candle.close:
                raise ValueError("invalid candle high")
            if candle.low > candle.open or candle.low > candle.close:
                raise ValueError("invalid candle low")
            if candle.volume < 0:
                raise ValueError("candle volume cannot be negative")
            if index and candle.end < candles[index - 1].end:
                raise ValueError("candles must be chronological")
            if index and candle.session_date is not None and candles[index - 1].session_date is not None:
                if candle.session_date != candles[index - 1].session_date:
                    raise ValueError("candles must belong to one trading session date")
