from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.backtest.engine import BacktestEvent
from advance_system.domain.market_events import QuoteEvent
from advance_system.domain.versioning import (
    CURRENT_CONTRACT_VERSIONS,
    ContractName,
    validate_contract_version,
)
from advance_system.oms.state_machine import OmsOrder, OmsState, OrderStateMachine
from advance_system.opportunity.engine import Opportunity


def test_contract_registry_declares_version_one_for_core_contracts():
    assert CURRENT_CONTRACT_VERSIONS == {
        ContractName.QUOTE_EVENT: 1,
        ContractName.OPPORTUNITY: 1,
        ContractName.ORDER: 1,
        ContractName.BACKTEST_EVENT: 1,
    }


def test_supported_contract_version_is_accepted():
    for contract, version in CURRENT_CONTRACT_VERSIONS.items():
        validate_contract_version(contract, version)


def test_unknown_contract_version_is_rejected():
    with pytest.raises(ValueError, match="unsupported quote_event contract_version"):
        validate_contract_version(ContractName.QUOTE_EVENT, 2)


def test_quote_event_defaults_to_v1_without_changing_existing_constructor_shape():
    event = QuoteEvent("NSE:TEST", datetime.now(timezone.utc), Decimal("100"))
    assert event.contract_version == 1
    event.validate()


def test_opportunity_defaults_to_v1():
    opportunity = Opportunity(
        "opp-1",
        "NSE:TEST",
        "BREAKOUT",
        "breakout_continuation",
        "1.0",
        "UP",
        Decimal("100"),
        Decimal("99"),
        Decimal("102"),
        Decimal("2"),
        (),
    )
    assert opportunity.contract_version == 1
    opportunity.validate()


def test_backtest_event_defaults_to_v1():
    event = BacktestEvent(datetime.now(timezone.utc), "NSE:TEST", Decimal("100"))
    assert event.contract_version == 1
    event.validate()


def test_invalid_contract_version_is_rejected_by_contract_validation():
    event = QuoteEvent(
        "NSE:TEST",
        datetime.now(timezone.utc),
        Decimal("100"),
        contract_version=99,
    )
    with pytest.raises(ValueError, match="unsupported quote_event contract_version"):
        event.validate()


def test_oms_contract_version_is_independent_from_transition_version():
    order = OmsOrder("order-1", "NSE:TEST", 10)
    transitioned = OrderStateMachine().transition(order, OmsState.CANDIDATE)

    assert order.contract_version == 1
    assert transitioned.contract_version == 1
    assert order.version == 0
    assert transitioned.version == 1


def test_oms_rejects_unsupported_contract_version_before_transition():
    order = OmsOrder("order-1", "NSE:TEST", 10, contract_version=2)
    with pytest.raises(ValueError, match="unsupported order contract_version"):
        OrderStateMachine().transition(order, OmsState.CANDIDATE)
