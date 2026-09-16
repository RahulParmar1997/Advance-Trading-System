import pytest

from advance_system.oms.idempotency import PaperOrderGateway
from advance_system.oms.state_machine import OmsOrder, OmsState, OmsTransitionError, OrderStateMachine


def make_order() -> OmsOrder:
    return OmsOrder(order_id="o-1", instrument="NSE_EQ|TEST", quantity=10)


def test_canonical_lifecycle_and_partial_fill() -> None:
    machine = OrderStateMachine()
    order = make_order()
    for state in (OmsState.CANDIDATE, OmsState.QUALIFIED, OmsState.RISK_CHECK, OmsState.ORDER_PENDING):
        order = machine.transition(order, state)
    order = machine.transition(order, OmsState.PARTIALLY_FILLED, filled_quantity=4)
    assert order.filled_quantity == 4
    order = machine.transition(order, OmsState.FILLED, filled_quantity=10)
    assert order.state is OmsState.FILLED


def test_invalid_transition_is_rejected() -> None:
    with pytest.raises(OmsTransitionError):
        OrderStateMachine().transition(make_order(), OmsState.FILLED)


def test_fill_quantity_is_monotonic() -> None:
    machine = OrderStateMachine()
    order = machine.transition(make_order(), OmsState.CANDIDATE)
    order = machine.transition(order, OmsState.QUALIFIED)
    order = machine.transition(order, OmsState.RISK_CHECK)
    order = machine.transition(order, OmsState.ORDER_PENDING)
    order = machine.transition(order, OmsState.PARTIALLY_FILLED, filled_quantity=5)
    with pytest.raises(ValueError):
        machine.transition(order, OmsState.PARTIALLY_FILLED, filled_quantity=3)


def test_paper_gateway_is_idempotent() -> None:
    gateway = PaperOrderGateway()
    first = gateway.submit(make_order(), client_key="opportunity-1")
    second = gateway.submit(make_order(), client_key="opportunity-1")
    assert first.replayed is False
    assert second.replayed is True
    assert second.order == first.order


def test_different_client_key_cannot_reuse_order_id() -> None:
    gateway = PaperOrderGateway()
    gateway.submit(make_order(), client_key="key-1")
    with pytest.raises(ValueError, match="duplicate order_id"):
        gateway.submit(make_order(), client_key="key-2")


def test_client_key_collision_with_different_order_fails_closed() -> None:
    gateway = PaperOrderGateway()
    gateway.submit(make_order(), client_key="opportunity-1")
    different_order = OmsOrder(order_id="o-2", instrument="NSE_EQ|TEST", quantity=10)

    with pytest.raises(ValueError, match="client_key already bound to a different order_id"):
        gateway.submit(different_order, client_key="opportunity-1")
