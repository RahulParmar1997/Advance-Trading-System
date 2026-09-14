from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.backtest.engine import BacktestEvent, EventDrivenBacktester, FillPolicy


class OneShotStrategy:
    def __init__(self) -> None:
        self.done = False

    def on_event(self, event: BacktestEvent) -> int:
        if self.done:
            return 0
        self.done = True
        return 10


class BuyThenSell:
    def on_event(self, event: BacktestEvent) -> int:
        return 10 if event.price == Decimal("100") else -10


def test_events_are_processed_chronologically() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = EventDrivenBacktester().run(
        [BacktestEvent(base + timedelta(minutes=1), "NSE_EQ|TEST", Decimal("100")), BacktestEvent(base, "NSE_EQ|TEST", Decimal("90"))],
        OneShotStrategy(),
        starting_cash=Decimal("10000"),
    )
    assert result.fills[0].price == Decimal("90")
    assert result.ending_cash == Decimal("9100")


def test_costs_and_slippage_are_applied() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = EventDrivenBacktester().run(
        [BacktestEvent(base, "NSE_EQ|TEST", Decimal("100"))],
        OneShotStrategy(),
        starting_cash=Decimal("10000"),
        fee_bps=Decimal("10"),
        slippage_bps=Decimal("10"),
    )
    assert result.fills[0].price == Decimal("100.1")
    assert result.fills[0].fee == Decimal("1.001")


def test_round_trip_realizes_pnl_and_marks_equity() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = EventDrivenBacktester().run(
        [BacktestEvent(base, "NSE_EQ|TEST", Decimal("100")), BacktestEvent(base + timedelta(minutes=1), "NSE_EQ|TEST", Decimal("110"))],
        BuyThenSell(),
        starting_cash=Decimal("10000"),
    )
    assert result.realized_pnl == Decimal("100")
    assert result.ending_cash == Decimal("10100")
    assert result.ending_position == 0
    assert result.ending_equity == Decimal("10100")


def test_partial_fill_policy_splits_fills() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = EventDrivenBacktester().run(
        [BacktestEvent(base, "NSE_EQ|TEST", Decimal("100"))],
        OneShotStrategy(),
        starting_cash=Decimal("10000"),
        max_fill_quantity=4,
    )
    assert len(result.fills) == 3
    assert [fill.quantity for fill in result.fills] == [4, 4, 2]


def test_latency_uses_next_observable_event() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = EventDrivenBacktester().run(
        [
            BacktestEvent(base, "NSE_EQ|TEST", Decimal("100")),
            BacktestEvent(base + timedelta(seconds=5), "NSE_EQ|TEST", Decimal("105")),
        ],
        OneShotStrategy(),
        starting_cash=Decimal("10000"),
        latency=timedelta(seconds=1),
    )
    assert result.fills[0].price == Decimal("105")


def test_fill_policy_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        FillPolicy(max_fill_quantity=0).validate()
    with pytest.raises(ValueError):
        EventDrivenBacktester().run([], OneShotStrategy(), starting_cash=Decimal("100"), fee_bps=Decimal("-1"))
