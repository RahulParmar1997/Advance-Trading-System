from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Protocol

from advance_system.reconciliation.contracts import (
    BrokerFill,
    BrokerOrderSnapshot,
    FillSide,
)


class UpstoxOrderApi(Protocol):
    """Minimal injected boundary for the Upstox order APIs."""

    async def get_order_details(self, order_id: str) -> Mapping[str, Any]:
        ...

    async def get_order_fills(self, order_id: str) -> list[Mapping[str, Any]]:
        ...


@dataclass(frozen=True, slots=True)
class UpstoxReconciliationAdapter:
    """Translate authoritative Upstox order/fill responses into broker-neutral contracts."""

    api: UpstoxOrderApi

    async def fetch_order_snapshot(self, order_id: str) -> BrokerOrderSnapshot:
        if not order_id.strip():
            raise ValueError("order_id is required")
        raw = await self.api.get_order_details(order_id)
        return parse_upstox_order_snapshot(raw)

    async def fetch_fills(self, order_id: str) -> tuple[BrokerFill, ...]:
        if not order_id.strip():
            raise ValueError("order_id is required")
        raw_fills = await self.api.get_order_fills(order_id)
        fills = tuple(parse_upstox_fill(item) for item in raw_fills)
        if any(fill.order_id != order_id for fill in fills):
            raise ValueError("Upstox fill order identity mismatch")
        return fills


def parse_upstox_order_snapshot(payload: Mapping[str, Any]) -> BrokerOrderSnapshot:
    order_id = _required_text(payload, "order_id")
    status = _required_text(payload, "status")
    filled_quantity = _required_int(payload, "filled_quantity")
    average_raw = payload.get("average_fill_price")
    average = None if average_raw in (None, "") else _decimal(average_raw, "average_fill_price")
    snapshot = BrokerOrderSnapshot(order_id, status, filled_quantity, average)
    if snapshot.filled_quantity < 0:
        raise ValueError("filled_quantity cannot be negative")
    if snapshot.average_fill_price is not None and snapshot.average_fill_price <= 0:
        raise ValueError("average_fill_price must be positive")
    return snapshot


def parse_upstox_fill(payload: Mapping[str, Any]) -> BrokerFill:
    fill = BrokerFill(
        fill_id=_required_text(payload, "trade_id", fallback="fill_id"),
        order_id=_required_text(payload, "order_id"),
        instrument=_required_text(payload, "instrument_token", fallback="instrument"),
        side=FillSide(_required_text(payload, "transaction_type", fallback="side").upper()),
        quantity=_required_int(payload, "quantity"),
        price=_decimal(payload.get("average_price", payload.get("price")), "price"),
        timestamp=_parse_timestamp(payload.get("exchange_timestamp", payload.get("timestamp"))),
    )
    fill.validate()
    return fill


def _required_text(payload: Mapping[str, Any], key: str, *, fallback: str | None = None) -> str:
    value = payload.get(key)
    if (not isinstance(value, str) or not value.strip()) and fallback is not None:
        value = payload.get(fallback)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing required Upstox field: {key}")
    return value.strip()


def _required_int(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or value is None:
        raise ValueError(f"missing required Upstox field: {key}")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid Upstox integer field: {key}") from exc


def _decimal(value: Any, field: str) -> Decimal:
    if value in (None, ""):
        raise ValueError(f"missing required Upstox field: {field}")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid Upstox decimal field: {field}") from exc


def _parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("missing required Upstox timestamp")
    raw = value.strip().replace("Z", "+00:00")
    try:
        timestamp = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError("invalid Upstox timestamp") from exc
    if timestamp.tzinfo is None:
        raise ValueError("Upstox timestamp must be timezone-aware")
    return timestamp
