from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from advance_system.domain.versioning import ContractName, validate_contract_version


class OmsState(StrEnum):
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
    REJECTED = "REJECTED"


_ALLOWED: dict[OmsState, frozenset[OmsState]] = {
    OmsState.SCANNED: frozenset({OmsState.CANDIDATE, OmsState.REJECTED}),
    OmsState.CANDIDATE: frozenset({OmsState.QUALIFIED, OmsState.REJECTED}),
    OmsState.QUALIFIED: frozenset({OmsState.RISK_CHECK, OmsState.REJECTED}),
    OmsState.RISK_CHECK: frozenset({OmsState.ORDER_PENDING, OmsState.REJECTED}),
    OmsState.ORDER_PENDING: frozenset({OmsState.PARTIALLY_FILLED, OmsState.FILLED, OmsState.REJECTED}),
    OmsState.PARTIALLY_FILLED: frozenset({OmsState.PARTIALLY_FILLED, OmsState.FILLED, OmsState.EXIT}),
    OmsState.FILLED: frozenset({OmsState.MANAGED, OmsState.EXIT}),
    OmsState.MANAGED: frozenset({OmsState.SCALE_OUT, OmsState.EXIT}),
    OmsState.SCALE_OUT: frozenset({OmsState.MANAGED, OmsState.EXIT}),
    OmsState.EXIT: frozenset({OmsState.CLOSED}),
    OmsState.CLOSED: frozenset(),
    OmsState.REJECTED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class OmsOrder:
    """Canonical order lifecycle contract.

    ``version`` is the optimistic/lifecycle transition counter. It is distinct
    from ``contract_version``, which identifies the serialized schema.
    """

    order_id: str
    instrument: str
    quantity: int
    state: OmsState = OmsState.SCANNED
    filled_quantity: int = 0
    version: int = 0
    contract_version: int = 1


class OmsTransitionError(RuntimeError):
    pass


class OrderStateMachine:
    """Pure canonical OMS state transitions; no broker/network side effects."""

    def transition(self, order: OmsOrder, target: OmsState, *, filled_quantity: int | None = None) -> OmsOrder:
        validate_contract_version(ContractName.ORDER, order.contract_version)
        if not order.order_id or not order.instrument:
            raise ValueError("order_id and instrument are required")
        if order.quantity <= 0:
            raise ValueError("quantity must be positive")
        if order.filled_quantity < 0 or order.filled_quantity > order.quantity:
            raise ValueError("filled_quantity is outside order quantity")
        if target not in _ALLOWED[order.state]:
            raise OmsTransitionError(f"invalid OMS transition: {order.state} -> {target}")

        new_filled = order.filled_quantity if filled_quantity is None else filled_quantity
        if new_filled < order.filled_quantity or new_filled > order.quantity:
            raise ValueError("filled_quantity must be monotonic and within order quantity")
        if target is OmsState.PARTIALLY_FILLED and not 0 < new_filled < order.quantity:
            raise ValueError("partial fill requires quantity strictly between zero and total")
        if target is OmsState.FILLED and new_filled != order.quantity:
            raise ValueError("filled state requires full quantity")
        return replace(order, state=target, filled_quantity=new_filled, version=order.version + 1)
