from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.market.breadth import (
    ConstituentObservation,
    InstitutionalFlowObservation,
    InstitutionalSegment,
    build_breadth_snapshot,
    build_institutional_flow_snapshot,
    build_sector_breadth,
    build_sector_rotation,
)

OBSERVED_AT = datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc)


def observation(instrument: str, sector: str, previous: str, close: str, volume: int) -> ConstituentObservation:
    return ConstituentObservation(instrument, sector, OBSERVED_AT, Decimal(previous), Decimal(close), volume)


def test_breadth_is_deterministic_and_separates_up_down_volume() -> None:
    snapshot = build_breadth_snapshot(
        [
            observation("B", "BANK", "100", "99", 200),
            observation("A", "IT", "100", "102", 300),
            observation("C", "IT", "100", "100", 50),
        ]
    )
    assert snapshot.advances == 1
    assert snapshot.declines == 1
    assert snapshot.unchanged == 1
    assert snapshot.net_breadth == 0
    assert snapshot.breadth_percent == Decimal("33.33333333333333333333333333")
    assert snapshot.up_volume == 300
    assert snapshot.down_volume == 200
    assert snapshot.advance_ratio == Decimal("1")


def test_sector_breadth_and_rotation_use_only_observed_constituent_prices() -> None:
    observations = [
        observation("BANK1", "BANK", "100", "103", 100),
        observation("BANK2", "BANK", "100", "99", 100),
        observation("IT1", "IT", "100", "105", 100),
    ]
    sectors = build_sector_breadth(observations)
    assert [(item.sector, item.advances, item.declines) for item in sectors] == [("BANK", 1, 1), ("IT", 1, 0)]
    rotation = build_sector_rotation(observations, benchmark_return_pct=Decimal("1"))
    assert rotation[0].sector == "IT"
    assert rotation[0].relative_strength_pct == Decimal("4")
    assert rotation[0].rank == 1


def test_institutional_flow_is_explicit_observed_input_not_inferred() -> None:
    snapshot = build_institutional_flow_snapshot(
        [
            InstitutionalFlowObservation(InstitutionalSegment.FII, OBSERVED_AT, Decimal("125.50")),
            InstitutionalFlowObservation(InstitutionalSegment.DII, OBSERVED_AT, Decimal("-40.25")),
        ]
    )
    assert snapshot.fii_net_value == Decimal("125.50")
    assert snapshot.dii_net_value == Decimal("-40.25")
    assert snapshot.total_net_value == Decimal("85.25")


def test_rejects_mixed_timestamps_duplicates_and_invalid_prices() -> None:
    with pytest.raises(ValueError, match="same observation timestamp"):
        build_breadth_snapshot(
            [observation("A", "IT", "100", "101", 10), ConstituentObservation("B", "IT", OBSERVED_AT.replace(minute=1), Decimal("100"), Decimal("101"), 10)]
        )
    with pytest.raises(ValueError, match="duplicate instrument"):
        build_breadth_snapshot([observation("A", "IT", "100", "101", 10), observation("A", "BANK", "100", "99", 20)])
    with pytest.raises(ValueError, match="prices must be positive"):
        build_breadth_snapshot([observation("A", "IT", "100", "0", 10)])


def test_zero_denominators_are_explicitly_none() -> None:
    snapshot = build_breadth_snapshot([observation("A", "IT", "100", "101", 10)])
    assert snapshot.advance_ratio is None
    assert snapshot.up_down_volume_ratio is None


def test_institutional_flow_rejects_mixed_timestamps() -> None:
    with pytest.raises(ValueError, match="same observation timestamp"):
        build_institutional_flow_snapshot(
            [
                InstitutionalFlowObservation(InstitutionalSegment.FII, OBSERVED_AT, Decimal("1")),
                InstitutionalFlowObservation(InstitutionalSegment.DII, OBSERVED_AT.replace(minute=1), Decimal("2")),
            ]
        )
