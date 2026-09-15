from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum
from typing import Iterable


class InstitutionalSegment(StrEnum):
    FII = "FII"
    DII = "DII"


@dataclass(frozen=True, slots=True)
class ConstituentObservation:
    """Authoritative constituent observation; all analytics are derived from these fields."""

    instrument: str
    sector: str
    observed_at: datetime
    previous_close: Decimal
    close: Decimal
    volume: int

    def validate(self) -> None:
        if not self.instrument.strip() or not self.sector.strip():
            raise ValueError("instrument and sector are required")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.previous_close <= 0 or self.close <= 0:
            raise ValueError("prices must be positive")
        if self.volume < 0:
            raise ValueError("volume cannot be negative")

    @property
    def return_pct(self) -> Decimal:
        self.validate()
        return (self.close - self.previous_close) / self.previous_close * Decimal("100")


@dataclass(frozen=True, slots=True)
class BreadthSnapshot:
    observed_at: datetime
    total: int
    advances: int
    declines: int
    unchanged: int
    advance_ratio: Decimal | None
    breadth_percent: Decimal
    net_breadth: int
    up_volume: int
    down_volume: int
    up_down_volume_ratio: Decimal | None


@dataclass(frozen=True, slots=True)
class SectorBreadth:
    sector: str
    total: int
    advances: int
    declines: int
    unchanged: int
    breadth_percent: Decimal
    net_breadth: int
    average_return_pct: Decimal


@dataclass(frozen=True, slots=True)
class SectorRotation:
    sector: str
    breadth_percent: Decimal
    sector_return_pct: Decimal
    relative_strength_pct: Decimal | None
    rank: int


@dataclass(frozen=True, slots=True)
class InstitutionalFlowObservation:
    """Observed institutional flow; never inferred from price or volume."""

    segment: InstitutionalSegment
    observed_at: datetime
    net_value: Decimal

    def validate(self) -> None:
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")


@dataclass(frozen=True, slots=True)
class InstitutionalFlowSnapshot:
    observed_at: datetime
    fii_net_value: Decimal
    dii_net_value: Decimal
    total_net_value: Decimal


def _validate_observations(observations: Iterable[ConstituentObservation]) -> tuple[ConstituentObservation, ...]:
    selected = tuple(observations)
    if not selected:
        raise ValueError("constituent observations cannot be empty")
    for observation in selected:
        observation.validate()
    timestamps = {observation.observed_at.astimezone(timezone.utc) for observation in selected}
    if len(timestamps) != 1:
        raise ValueError("all constituent observations must share the same observation timestamp")
    instruments = [observation.instrument.strip() for observation in selected]
    if len(set(instruments)) != len(instruments):
        raise ValueError("duplicate instrument observation")
    return tuple(sorted(selected, key=lambda item: item.instrument.strip()))


def build_breadth_snapshot(observations: Iterable[ConstituentObservation]) -> BreadthSnapshot:
    selected = _validate_observations(observations)
    advances = sum(item.close > item.previous_close for item in selected)
    declines = sum(item.close < item.previous_close for item in selected)
    unchanged = len(selected) - advances - declines
    up_volume = sum(item.volume for item in selected if item.close > item.previous_close)
    down_volume = sum(item.volume for item in selected if item.close < item.previous_close)
    return BreadthSnapshot(
        observed_at=selected[0].observed_at,
        total=len(selected),
        advances=advances,
        declines=declines,
        unchanged=unchanged,
        advance_ratio=None if declines == 0 else Decimal(advances) / Decimal(declines),
        breadth_percent=Decimal(advances) / Decimal(len(selected)) * Decimal("100"),
        net_breadth=advances - declines,
        up_volume=up_volume,
        down_volume=down_volume,
        up_down_volume_ratio=None if down_volume == 0 else Decimal(up_volume) / Decimal(down_volume),
    )


def build_sector_breadth(observations: Iterable[ConstituentObservation]) -> tuple[SectorBreadth, ...]:
    selected = _validate_observations(observations)
    groups: dict[str, list[ConstituentObservation]] = {}
    for observation in selected:
        groups.setdefault(observation.sector.strip(), []).append(observation)
    result: list[SectorBreadth] = []
    for sector, items in groups.items():
        advances = sum(item.close > item.previous_close for item in items)
        declines = sum(item.close < item.previous_close for item in items)
        unchanged = len(items) - advances - declines
        result.append(
            SectorBreadth(
                sector=sector,
                total=len(items),
                advances=advances,
                declines=declines,
                unchanged=unchanged,
                breadth_percent=Decimal(advances) / Decimal(len(items)) * Decimal("100"),
                net_breadth=advances - declines,
                average_return_pct=sum((item.return_pct for item in items), Decimal("0")) / Decimal(len(items)),
            )
        )
    return tuple(sorted(result, key=lambda item: item.sector))


def build_sector_rotation(
    observations: Iterable[ConstituentObservation],
    *,
    benchmark_return_pct: Decimal | None = None,
) -> tuple[SectorRotation, ...]:
    sectors = build_sector_breadth(observations)
    ranked = sorted(
        sectors,
        key=lambda item: (
            -(item.average_return_pct - benchmark_return_pct) if benchmark_return_pct is not None else -item.average_return_pct,
            -item.breadth_percent,
            item.sector,
        ),
    )
    return tuple(
        SectorRotation(
            sector=item.sector,
            breadth_percent=item.breadth_percent,
            sector_return_pct=item.average_return_pct,
            relative_strength_pct=(item.average_return_pct - benchmark_return_pct if benchmark_return_pct is not None else None),
            rank=index,
        )
        for index, item in enumerate(ranked, start=1)
    )


def build_institutional_flow_snapshot(
    observations: Iterable[InstitutionalFlowObservation],
) -> InstitutionalFlowSnapshot:
    selected = tuple(observations)
    if not selected:
        raise ValueError("institutional flow observations cannot be empty")
    for observation in selected:
        observation.validate()
    timestamps = {item.observed_at.astimezone(timezone.utc) for item in selected}
    if len(timestamps) != 1:
        raise ValueError("all institutional flow observations must share the same observation timestamp")
    fii = sum((item.net_value for item in selected if item.segment == InstitutionalSegment.FII), Decimal("0"))
    dii = sum((item.net_value for item in selected if item.segment == InstitutionalSegment.DII), Decimal("0"))
    return InstitutionalFlowSnapshot(
        observed_at=selected[0].observed_at,
        fii_net_value=fii,
        dii_net_value=dii,
        total_net_value=fii + dii,
    )
