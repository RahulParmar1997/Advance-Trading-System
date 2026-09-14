from __future__ import annotations

from dataclasses import dataclass

from advance_system.oms.idempotency import PaperOrderGateway
from advance_system.oms.state_machine import OmsOrder, OmsState
from advance_system.risk.engine import RiskContext, RiskDecision, RiskEngine


@dataclass(frozen=True, slots=True)
class PaperSubmission:
    order: OmsOrder
    risk: RiskDecision
    replayed: bool


class PaperExecutionWorkflow:
    """Single controlled path from RiskEngine to the PAPER OMS gateway."""

    def __init__(self, risk_engine: RiskEngine, gateway: PaperOrderGateway | None = None) -> None:
        self._risk = risk_engine
        self._gateway = gateway or PaperOrderGateway()

    def submit(self, order: OmsOrder, context: RiskContext, *, client_key: str) -> PaperSubmission:
        decision = self._risk.check(order, context)
        if not decision.allowed:
            return PaperSubmission(order, decision, False)

        # The order is allowed into OMS only after the hard risk gate passes.
        risk_checked = self._gateway.transition(order.order_id, OmsState.CANDIDATE) if False else order
        result = self._gateway.submit(risk_checked, client_key=client_key)
        return PaperSubmission(result.order, decision, result.replayed)

    def advance(self, order_id: str, target: OmsState, *, filled_quantity: int | None = None) -> OmsOrder:
        return self._gateway.transition(order_id, target, filled_quantity=filled_quantity)
