from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.backtest.engine import BacktestEvent
from advance_system.backtest.validation import WalkForwardValidator


class NoTrade:
    def on_event(self, event: BacktestEvent) -> int:
        return 0


def events(count: int) -> list[BacktestEvent]:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [BacktestEvent(base + timedelta(minutes=i), "NSE_EQ|TEST", Decimal("100")) for i in range(count)]


def test_windows_are_strictly_chronological_and_disjoint() -> None:
    source = events(6)
    result = WalkForwardValidator().windows(source, train_size=3, test_size=2)
    assert len(result) == 1
    assert result[0].train == tuple(source[:3])
    assert result[0].test == tuple(source[3:5])
    assert result[0].train[-1].timestamp < result[0].test[0].timestamp


def test_multiple_windows_roll_forward() -> None:
    result = WalkForwardValidator().windows(events(8), train_size=3, test_size=2, step=2)
    assert len(result) == 2
    assert result[0].train[-1].timestamp < result[0].test[0].timestamp
    assert result[1].train[-1].timestamp < result[1].test[0].timestamp
    assert result[1].test[0].timestamp > result[0].test[0].timestamp


def test_invalid_window_sizes_are_rejected() -> None:
    with pytest.raises(ValueError):
        WalkForwardValidator().windows(events(5), train_size=0, test_size=2)


def test_run_uses_only_test_events_for_backtest() -> None:
    result = WalkForwardValidator().run(
        events(6),
        lambda train: NoTrade(),
        train_size=3,
        test_size=2,
        starting_cash=Decimal("1000"),
    )
    assert len(result) == 1
    assert result[0].train_events == 3
    assert result[0].test_events == 2
    assert result[0].test_result.fills == ()
