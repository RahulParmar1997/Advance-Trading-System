from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.backtest.engine import BacktestEvent, EventDrivenBacktester


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


def events() -> list[BacktestEvent]:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [
        BacktestEvent(base + timedelta(minutes=1), "NSE_EQ|TEST", Decimal("100")),
        BacktestEvent(base, "NSE_EQ|TEST", Decimal("90")),
    ]


def test_events_are_processed_chronologically() -> None:
    result = EventDrivenBacktester().run(events(), OneShotStrategy(), starting_cash=Decimal("10000"))
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


def test_round_trip_realizes_pnl() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = EventDrivenBacktester().run(
        [
            BacktestEvent(base, "NSE_EQ|TEST", Decimal("100")),
            BacktestEvent(base + timedelta(minutes=1), "NSE_EQ|TEST", Decimal("110")),
        ],
        BuyThenSell(),
        starting_cash=Decimal("10000"),
    )
    assert result.realized_pnl == Decimal("100")
    assert result.ending_cash == Decimal("10100")


def test_negative_execution_costs_are_rejected() -> None:
    with pytest.raises(ValueError):
        EventDrivenBacktester().run([], OneShotStrategy(), starting_cash=Decimal("100"), fee_bps=Decimal("-1"))
