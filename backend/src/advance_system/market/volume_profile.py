from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from advance_system.market.candle_engine import Candle


@dataclass(frozen=True, slots=True)
class VolumeProfileConfig:
    """Explicit price-bucket configuration for candle-volume profiles."""

    price_step: Decimal = Decimal("1")

    def validate(self) -> None:
        if self.price_step <= 0:
            raise ValueError("price_step must be positive")


@dataclass(frozen=True, slots=True)
class VolumeLevel:
    price: Decimal
    volume: int


@dataclass(frozen=True, slots=True)
class VolumeProfile:
    instrument: str
    session_date: object | None
    levels: tuple[VolumeLevel, ...]
    total_volume: int
    point_of_control: Decimal | None
    value_area_low: Decimal | None
    value_area_high: Decimal | None


class VolumeProfileEngine:
    """Build a deterministic volume-at-price approximation from completed candles.

    Candle volume is allocated to the candle's close-price bucket. This is not
    claimed to be tick-level volume-at-price; true order-flow requires trade
    prints/quantities that are not part of the canonical QuoteEvent contract.
    """

    def __init__(self, config: VolumeProfileConfig | None = None) -> None:
        self.config = config or VolumeProfileConfig()
        self.config.validate()

    def build(self, candles: Sequence[Candle], *, value_area_fraction: Decimal = Decimal("0.70")) -> VolumeProfile:
        if not candles:
            raise ValueError("candles cannot be empty")
        if not Decimal("0") < value_area_fraction <= Decimal("1"):
            raise ValueError("value_area_fraction must be between 0 and 1")
        instrument = candles[0].instrument
        session_date = candles[0].session_date
        if any(c.instrument != instrument for c in candles):
            raise ValueError("volume profile requires one instrument")
        if any(c.session_date != session_date for c in candles):
            raise ValueError("volume profile cannot mix session dates")
        buckets: dict[Decimal, int] = {}
        for candle in candles:
            if candle.volume < 0:
                raise ValueError("candle volume cannot be negative")
            bucket = (candle.close / self.config.price_step).to_integral_value() * self.config.price_step
            buckets[bucket] = buckets.get(bucket, 0) + candle.volume
        levels = tuple(VolumeLevel(price, buckets[price]) for price in sorted(buckets))
        total = sum(level.volume for level in levels)
        if not levels or total == 0:
            return VolumeProfile(instrument, session_date, levels, total, None, None, None)
        poc = max(levels, key=lambda level: (level.volume, -level.price)).price
        target = Decimal(total) * value_area_fraction
        poc_index = next(i for i, level in enumerate(levels) if level.price == poc)
        selected = {poc_index}
        accumulated = Decimal(levels[poc_index].volume)
        left = poc_index - 1
        right = poc_index + 1
        while accumulated < target and (left >= 0 or right < len(levels)):
            left_volume = levels[left].volume if left >= 0 else -1
            right_volume = levels[right].volume if right < len(levels) else -1
            if right_volume > left_volume:
                selected.add(right)
                accumulated += Decimal(right_volume)
                right += 1
            else:
                selected.add(left)
                accumulated += Decimal(left_volume)
                left -= 1
        selected_prices = [levels[i].price for i in selected]
        return VolumeProfile(
            instrument,
            session_date,
            levels,
            total,
            poc,
            min(selected_prices),
            max(selected_prices),
        )
