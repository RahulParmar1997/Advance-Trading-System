from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.market.candle_engine import Candle
from advance_system.market.wyckoff import WyckoffEvent, WyckoffEngine


BASE = datetime(2026, 1, 5, 9, 15, tzinfo=timezone.utc)


def candle(i: int, low: str, high: str, close: str, volume: int, open_: str | None = None, instrument: str = "NSE_EQ|TEST") -> Candle:
    start = BASE + timedelta(minutes=i)
    return Candle(
        instrument,
        start,
        start + timedelta(minutes=1),
        Decimal(open_ or close),
        Decimal(high),
        Decimal(low),
        Decimal(close),
        volume,
    )


def history() -> list[Candle]:
    return [candle(i, "99", "101", "100", 100) for i in range(5)]


def test_spring_uses_prior_support_and_explicit_volume() -> None:
    candles = history() + [candle(5, "98", "101", "100.5", 250, "98.5")]
    observation = WyckoffEngine().observe(candles)
    assert observation.event is WyckoffEvent.SPRING
    assert "close reclaimed prior support" in observation.evidence
    assert observation.features is not None
    assert observation.features.volume_ratio == Decimal("2.5")


def test_upthrust_is_deterministic() -> None:
    candles = history() + [candle(5, "99", "102", "100.5", 250, "101.5")]
    observation = WyckoffEngine().observe(candles)
    assert observation.event is WyckoffEvent.UPTHRUST


def test_sign_of_strength_requires_wide_high_volume_breakout() -> None:
    candles = history() + [candle(5, "99.5", "104", "103.5", 250, "100")]
    observation = WyckoffEngine().observe(candles)
    assert observation.event is WyckoffEvent.SIGN_OF_STRENGTH


def test_sign_of_weakness_requires_wide_high_volume_breakdown() -> None:
    candles = history() + [candle(5, "96", "100.5", "96.5", 250, "100")]
    observation = WyckoffEngine().observe(candles)
    assert observation.event is WyckoffEvent.SIGN_OF_WEAKNESS


def test_insufficient_history_is_explicit() -> None:
    observation = WyckoffEngine().observe(history()[:5])
    assert observation.event is WyckoffEvent.INSUFFICIENT_DATA
    assert observation.features is None


def test_future_candle_cannot_change_prior_observation() -> None:
    candles = history() + [candle(5, "99", "101", "100", 100)]
    engine = WyckoffEngine()
    before = engine.observe(candles)
    future = candle(6, "80", "120", "110", 10000)
    after = engine.observe(candles + [future])
    assert before.observed_at == candles[-1].end
    assert before.event is WyckoffEvent.NONE
    assert after.observed_at == future.end


def test_out_of_order_and_mixed_instrument_inputs_fail_closed() -> None:
    candles = history()
    with pytest.raises(ValueError, match="chronological"):
        WyckoffEngine().observe([candles[0], candles[2], candles[1], *candles[3:]])
    with pytest.raises(ValueError, match="one instrument"):
        WyckoffEngine().observe(candles[:-1] + [candle(4, "99", "101", "100", 100, instrument="NSE_EQ|OTHER")])


def test_zero_current_volume_is_rejected_instead_of_inferred() -> None:
    with pytest.raises(ValueError, match="positive current/prior spread and volume"):
        WyckoffEngine().observe(history() + [candle(5, "98", "101", "100", 0)])


def test_invalid_candle_ohlc_is_rejected() -> None:
    with pytest.raises(ValueError, match="invalid candle high"):
        WyckoffEngine().observe(history() + [candle(5, "99", "101", "102", 100)])
