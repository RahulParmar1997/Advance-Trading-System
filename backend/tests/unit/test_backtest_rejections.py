from datetime import datetime, timezone
from decimal import Decimal

from advance_system.backtest.engine import BacktestEvent, EventDrivenBacktester
from advance_system.backtest.rejections import RejectionPolicy, RejectionReason


class BuyTen:
    def on_event(self, event: BacktestEvent) -> int:
        return 10


def test_rejection_policy_validates_order_inputs() -> None:
    policy = RejectionPolicy()
    assert policy.validate(0, Decimal("100")) is RejectionReason.INVALID_QUANTITY
    assert policy.validate(1, Decimal("0")) is RejectionReason.INVALID_PRICE
    assert policy.validate(1, Decimal("100")) is None


def test_insufficient_cash_rejects_without_creating_a_fill() -> None:
    event = BacktestEvent(datetime(2026, 1, 1, tzinfo=timezone.utc), "NSE_EQ|TEST", Decimal("100"))
    result = EventDrivenBacktester().run([event], BuyTen(), starting_cash=Decimal("50"))
    assert result.fills == ()
    assert result.rejected_orders == 1
    assert result.ending_cash == Decimal("50")
