from datetime import date
from decimal import Decimal

import pytest

from advance_system.market.derivatives import DerivativeType, OptionChain, OptionType, parse_derivative_record


def option_record(instrument="NSE_FO|123", option_type="CE", strike="25000"):
    return {
        "instrument_key": instrument,
        "exchange": "NSE",
        "trading_symbol": "NIFTY",
        "instrument_type": option_type,
        "underlying_symbol": "NIFTY",
        "expiry": "2026-10-29",
        "strike_price": strike,
        "lot_size": "65",
        "tick_size": "0.05",
    }


def test_parse_option_contract():
    contract = parse_derivative_record(option_record())
    assert contract.derivative_type == DerivativeType.OPTION
    assert contract.option_type == OptionType.CALL
    assert contract.strike == Decimal("25000")
    assert contract.expiry == date(2026, 10, 29)
    assert contract.lot_size == 65


def test_parse_future_rejects_option_fields():
    record = option_record(option_type="FUT", strike="")
    contract = parse_derivative_record(record)
    assert contract.derivative_type == DerivativeType.FUTURE
    assert contract.strike is None
    assert contract.option_type is None


def test_missing_underlying_fails_closed():
    record = option_record()
    del record["underlying_symbol"]
    with pytest.raises(ValueError, match="underlying"):
        parse_derivative_record(record)


def test_option_chain_is_sorted_and_keyed():
    first = parse_derivative_record(option_record("B", "PE", "24900"))
    second = parse_derivative_record(option_record("A", "CE", "24900"))
    chain = OptionChain.build((first, second), underlying="NIFTY", expiry=date(2026, 10, 29))
    assert [c.instrument for c in chain.contracts] == ["A", "B"]


def test_option_chain_rejects_mismatched_expiry():
    contract = parse_derivative_record(option_record())
    with pytest.raises(ValueError, match="chain key"):
        OptionChain.build((contract,), underlying="NIFTY", expiry=date(2026, 11, 26))


def test_invalid_strike_fails():
    with pytest.raises(ValueError, match="strike"):
        parse_derivative_record(option_record(strike="0"))
