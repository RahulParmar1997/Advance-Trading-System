from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.market.order_flow import Aggressor, OrderFlowEngine, TradePrint


def trade(i: int, price: str, qty: int, side: Aggressor) -> TradePrint:
    return TradePrint("NSE_EQ|TEST", datetime(2026, 1, 5, 9, 15, tzinfo=timezone.utc) + timedelta(seconds=i), Decimal(price), qty, side)


def test_order_flow_aggregates_explicit_trade_sides():
    summary = OrderFlowEngine().summarize([
        trade(0, "100", 10, Aggressor.BUY),
        trade(1, "101", 7, Aggressor.SELL),
        trade(2, "101", 3, Aggressor.UNKNOWN),
    ])
    assert summary.buy_volume == 10
    assert summary.sell_volume == 7
    assert summary.unknown_volume == 3
    assert summary.delta == 3


def test_aggressor_inference_is_conservative():
    engine = OrderFlowEngine()
    assert engine.infer_aggressor(Decimal("101"), Decimal("100"), Decimal("101")) is Aggressor.BUY
    assert engine.infer_aggressor(Decimal("100"), Decimal("100"), Decimal("101")) is Aggressor.SELL
    assert engine.infer_aggressor(Decimal("100.5"), Decimal("100"), Decimal("101")) is Aggressor.UNKNOWN


def test_order_flow_rejects_non_chronological_or_mixed_trades():
    with pytest.raises(ValueError, match="chronological"):
        OrderFlowEngine().summarize([trade(2, "100", 1, Aggressor.BUY), trade(1, "100", 1, Aggressor.SELL)])
    other = TradePrint("NSE_EQ|OTHER", trade(0, "100", 1, Aggressor.BUY).timestamp, Decimal("100"), 1, Aggressor.BUY)
    with pytest.raises(ValueError, match="one instrument"):
        OrderFlowEngine().summarize([trade(0, "100", 1, Aggressor.BUY), other])
