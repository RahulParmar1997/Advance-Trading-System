from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.reconciliation.contracts import FillSide
from advance_system.reconciliation.upstox import (
    UpstoxReconciliationAdapter,
    parse_upstox_fill,
    parse_upstox_order_snapshot,
)


class FakeUpstoxApi:
    async def get_order_details(self, order_id: str):
        return {
            "order_id": order_id,
            "status": "complete",
            "filled_quantity": 10,
            "average_fill_price": "101.25",
        }

    async def get_order_fills(self, order_id: str):
        return [
            {
                "trade_id": "trade-1",
                "order_id": order_id,
                "instrument_token": "NSE_EQ|INE000000001",
                "transaction_type": "BUY",
                "quantity": 10,
                "average_price": "101.25",
                "exchange_timestamp": "2026-09-15T10:00:00+05:30",
            }
        ]


@pytest.mark.asyncio
async def test_adapter_translates_order_and_fills():
    adapter = UpstoxReconciliationAdapter(FakeUpstoxApi())
    snapshot = await adapter.fetch_order_snapshot("order-1")
    fills = await adapter.fetch_fills("order-1")

    assert snapshot.order_id == "order-1"
    assert snapshot.filled_quantity == 10
    assert snapshot.average_fill_price == Decimal("101.25")
    assert fills[0].fill_id == "trade-1"
    assert fills[0].side is FillSide.BUY
    assert fills[0].timestamp == datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc).replace(hour=10, minute=0)


def test_order_snapshot_rejects_negative_fill_quantity():
    with pytest.raises(ValueError, match="cannot be negative"):
        parse_upstox_order_snapshot({"order_id": "o", "status": "complete", "filled_quantity": -1})


def test_fill_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        parse_upstox_fill(
            {
                "trade_id": "t",
                "order_id": "o",
                "instrument_token": "i",
                "transaction_type": "BUY",
                "quantity": 1,
                "average_price": "10",
                "exchange_timestamp": "2026-09-15T10:00:00",
            }
        )


def test_fill_rejects_unknown_side():
    with pytest.raises(ValueError):
        parse_upstox_fill(
            {
                "trade_id": "t",
                "order_id": "o",
                "instrument_token": "i",
                "transaction_type": "HOLD",
                "quantity": 1,
                "average_price": "10",
                "exchange_timestamp": "2026-09-15T10:00:00+00:00",
            }
        )


class MismatchedFillApi(FakeUpstoxApi):
    async def get_order_fills(self, order_id: str):
        rows = await super().get_order_fills(order_id)
        rows[0]["order_id"] = "other-order"
        return rows


@pytest.mark.asyncio
async def test_adapter_rejects_fill_identity_mismatch():
    adapter = UpstoxReconciliationAdapter(MismatchedFillApi())
    with pytest.raises(ValueError, match="order identity mismatch"):
        await adapter.fetch_fills("order-1")


@pytest.mark.asyncio
async def test_adapter_rejects_empty_order_id():
    adapter = UpstoxReconciliationAdapter(FakeUpstoxApi())
    with pytest.raises(ValueError, match="order_id is required"):
        await adapter.fetch_order_snapshot(" ")
