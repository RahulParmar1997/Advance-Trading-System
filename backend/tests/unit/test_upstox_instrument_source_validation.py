import json

import pytest

from advance_system.adapters.upstox.instrument_source import (
    UpstoxInstrumentMasterConfig,
    UpstoxInstrumentMasterSource,
)


def _source(record: dict) -> UpstoxInstrumentMasterSource:
    payload = json.dumps([record]).encode()
    return UpstoxInstrumentMasterSource(
        UpstoxInstrumentMasterConfig("https://example.test/bod.json"),
        lambda _: payload,
    )


def _valid_record() -> dict:
    return {
        "segment": "NSE_EQ",
        "exchange": "NSE",
        "instrument_type": "EQ",
        "instrument_key": "NSE_EQ|INE002A01018",
        "trading_symbol": "RELIANCE",
    }


def test_source_rejects_non_string_instrument_identity() -> None:
    record = _valid_record()
    record["instrument_key"] = 123

    with pytest.raises(ValueError, match="instrument_key"):
        tuple(_source(record).fetch())


def test_source_rejects_blank_symbol() -> None:
    record = _valid_record()
    record["trading_symbol"] = "   "

    with pytest.raises(ValueError, match="trading_symbol"):
        tuple(_source(record).fetch())


def test_source_applies_domain_validation_before_returning_records() -> None:
    record = _valid_record()
    record["exchange"] = "nse"

    with pytest.raises(ValueError, match="exchange must be uppercase"):
        tuple(_source(record).fetch())
