from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.market.candle_engine import Candle
from advance_system.market.features import DisplacementConfig, FeatureEngine
from advance_system.market.session import SessionPhase


def candle(minute: int, low: str, high: str, close: str, *, open_price: str | None = None, session: bool = True) -> Candle:
    start = datetime(2026, 1, 5, 9, 15 + minute, tzinfo=timezone.utc)
    return Candle(
        instrument="NSE_EQ|TEST",
        start=start,
        end=start.replace(minute=start.minute + 1),
        open=Decimal(open_price if open_price is not None else low),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=100,
        session_date=start.date() if session else None,
        session_phase=SessionPhase.OPEN if session else None,
    )


def test_displacement_uses_only_prior_completed_candles():
    engine = FeatureEngine(DisplacementConfig(min_body_to_range=Decimal("0.7"), min_range_to_average=Decimal("1.5"), lookback=3))
    prior = [
        candle(0, "99", "101", "100.5", open_price="99.5"),
        candle(1, "99", "101", "99.5", open_price="100.5"),
        candle(2, "99", "101", "100.5", open_price="99.5"),
    ]
    current = candle(3, "99", "105", "104.5", open_price="99.5")

    features = engine.calculate(current, prior)

    assert features.body_to_range == Decimal("0.8333333333333333333333333333")
    assert features.average_prior_range == Decimal("2")
    assert features.range_to_average == Decimal("3")
    assert features.displacement is True
    assert features.displacement_direction == "UP"


def test_no_history_means_no_displacement():
    features = FeatureEngine().calculate(candle(0, "99", "105", "104", open_price="100"))

    assert features.average_prior_range is None
    assert features.range_to_average is None
    assert features.displacement is False
    assert features.displacement_direction == "NONE"


def test_directional_displacement_can_be_bearish():
    engine = FeatureEngine(DisplacementConfig(min_body_to_range=Decimal("0.7"), min_range_to_average=Decimal("1.5")))
    prior = [candle(i, "99", "101", "100", open_price="100") for i in range(5)]
    current = candle(5, "95", "101", "95.5", open_price="100.5")

    features = engine.calculate(current, prior)

    assert features.displacement is True
    assert features.displacement_direction == "DOWN"


def test_previous_candles_cannot_look_ahead_or_mix_instruments():
    engine = FeatureEngine()
    current = candle(2, "99", "101", "100", open_price="99.5")
    future = candle(3, "99", "101", "100", open_price="99.5")
    with pytest.raises(ValueError, match="precede"):
        engine.calculate(current, [future])

    other = Candle(
        "NSE_EQ|OTHER", future.start, future.end, future.open, future.high, future.low, future.close, future.volume,
        future.session_date, future.session_phase,
    )
    with pytest.raises(ValueError, match="one instrument"):
        engine.calculate(current, [other])


def test_session_metadata_must_be_complete_when_present():
    current = candle(0, "99", "101", "100", session=False)
    broken = Candle(
        current.instrument, current.start, current.end, current.open, current.high, current.low, current.close,
        current.volume, current.start.date(), None,
    )
    with pytest.raises(ValueError, match="session phase"):
        FeatureEngine().calculate(broken)
