from datetime import datetime, timezone
from decimal import Decimal

from advance_system.backtest.engine import BacktestEvent, EventDrivenBacktester
from advance_system.backtest.rejections import HistoricalLiquidity, RejectionPolicy, RejectionReason


class BuyOnce:
    def on_event(self, event: BacktestEvent) -> int:
        return 10 if event.timestamp.minute == 0 else 0


def event(minute: int, liquidity: HistoricalLiquidity | None = None) -> BacktestEvent:
    return BacktestEvent(datetime(2026, 1, 1, 9, minute, tzinfo=timezone.utc), "NSE:TEST", Decimal("100"), liquidity)


def test_no_liquidity_is_rejected() -> None:
    result = EventDrivenBacktester().run([event(0, HistoricalLiquidity(0)), event(1)], BuyOnce(), starting_cash=Decimal("10000"))
    assert result.fills == ()
    assert result.rejected_orders == 1


def test_historical_liquidity_causes_partial_fill() -> None:
    result = EventDrivenBacktester().run([event(0, HistoricalLiquidity(4)), event(1)], BuyOnce(), starting_cash=Decimal("10000"))
    assert len(result.fills) == 1
    assert result.fills[0].quantity == 4
    assert result.ending_position == 4


def test_participation_cap_is_observable_at_execution_event() -> None:
    result = EventDrivenBacktester().run(
        [event(0, HistoricalLiquidity(10, market_volume=20)), event(1, HistoricalLiquidity(10, market_volume=20))],
        BuyOnce(), starting_cash=Decimal("10000"), participation_rate=Decimal("0.25")
    )
    assert result.fills[0].quantity == 5


def test_rejection_policy_reports_participation_limit() -> None:
    qty, reason = RejectionPolicy().fill_quantity(10, HistoricalLiquidity(10, market_volume=1), participation_rate=Decimal("0.5"))
    assert qty == 0
    assert reason == RejectionReason.PARTICIPATION_LIMIT
