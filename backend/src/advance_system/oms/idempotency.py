from __future__ import annotations

from dataclasses import dataclass

from advance_system.oms.state_machine import OmsOrder, OmsState, OrderStateMachine


@dataclass(frozen=True, slots=True)
class SubmissionResult:
    order: OmsOrder
    replayed: bool


class PaperOrderGateway:
    """Idempotent in-memory PAPER gateway keyed by client order identity."""

    def __init__(self, state_machine: OrderStateMachine | None = None) -> None:
        self._machine = state_machine or OrderStateMachine()
        self._orders: dict[str, OmsOrder] = {}
        self._client_keys: dict[str, str] = {}

    def submit(self, order: OmsOrder, *, client_key: str) -> SubmissionResult:
        if not client_key.strip():
            raise ValueError("client_key is required")
        existing_id = self._client_keys.get(client_key)
        if existing_id is not None:
            return SubmissionResult(self._orders[existing_id], True)
        if order.order_id in self._orders:
            raise ValueError("duplicate order_id")
        self._orders[order.order_id] = order
        self._client_keys[client_key] = order.order_id
        return SubmissionResult(order, False)

    def transition(self, order_id: str, target: OmsState, *, filled_quantity: int | None = None) -> OmsOrder:
        order = self._orders[order_id]
        updated = self._machine.transition(order, target, filled_quantity=filled_quantity)
        self._orders[order_id] = updated
        return updated

    def get(self, order_id: str) -> OmsOrder:
        return self._orders[order_id]
