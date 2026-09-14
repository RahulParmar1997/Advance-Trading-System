from __future__ import annotations

from enum import StrEnum


class OrderState(StrEnum):
    SCANNED = "SCANNED"
    CANDIDATE = "CANDIDATE"
    QUALIFIED = "QUALIFIED"
    RISK_CHECK = "RISK_CHECK"
    ORDER_PENDING = "ORDER_PENDING"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    MANAGED = "MANAGED"
    SCALE_OUT = "SCALE_OUT"
    EXIT = "EXIT"
    CLOSED = "CLOSED"


ALLOWED_TRANSITIONS: dict[OrderState, set[OrderState]] = {
    OrderState.SCANNED: {OrderState.CANDIDATE},
    OrderState.CANDIDATE: {OrderState.QUALIFIED},
    OrderState.QUALIFIED: {OrderState.RISK_CHECK},
    OrderState.RISK_CHECK: {OrderState.ORDER_PENDING, OrderState.CLOSED},
    OrderState.ORDER_PENDING: {
        OrderState.PARTIALLY_FILLED,
        OrderState.FILLED,
        OrderState.CLOSED,
    },
    OrderState.PARTIALLY_FILLED: {OrderState.PARTIALLY_FILLED, OrderState.FILLED, OrderState.EXIT},
    OrderState.FILLED: {OrderState.MANAGED, OrderState.EXIT},
    OrderState.MANAGED: {OrderState.SCALE_OUT, OrderState.EXIT},
    OrderState.SCALE_OUT: {OrderState.MANAGED, OrderState.EXIT},
    OrderState.EXIT: {OrderState.CLOSED},
    OrderState.CLOSED: set(),
}


def transition(current: OrderState, target: OrderState) -> OrderState:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"invalid OMS transition: {current} -> {target}")
    return target
