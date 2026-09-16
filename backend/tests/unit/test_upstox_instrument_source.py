import json

import pytest

from advance_system.adapters.upstox.instrument_source import UpstoxInstrumentMasterConfig, UpstoxInstrumentMasterSource


def payload():
    return json.dumps([
        {
            "segment": "NSE_EQ",
            "name": "RELIANCE INDUSTRIES LTD",
            "exchange": "NSE",
            "instrument_type": "EQ",
            "instrument_key": "NSE_EQ|INE002A01018",
            "trading_symbol": "RELIANCE",
        }
    ]).encode()


def test_upstox_json_is_mapped_to_broker_neutral_record():
    source = UpstoxInstrumentMasterSource(UpstoxInstrumentMasterConfig("https://example.test/bod.json"), lambda _: payload())
    records = tuple(source.fetch())
    assert records[0].instrument == "NSE_EQ|INE002A01018"
    assert records[0].exchange == "NSE"
    assert records[0].symbol == "RELIANCE"
    assert records[0].asset_type == "EQ"


def test_malformed_payload_fails_closed():
    source = UpstoxInstrumentMasterSource(UpstoxInstrumentMasterConfig("https://example.test/bod.json"), lambda _: b"{")
    with pytest.raises(ValueError, match="invalid Upstox instrument master JSON"):
        source.fetch()


def test_non_array_payload_fails_closed():
    source = UpstoxInstrumentMasterSource(
        UpstoxInstrumentMasterConfig("https://example.test/bod.json"), lambda _: b"{}"
    )
    with pytest.raises(ValueError, match="JSON array"):
        source.fetch()


def test_missing_required_upstox_field_fails_closed():
    source = UpstoxInstrumentMasterSource(
        UpstoxInstrumentMasterConfig("https://example.test/bod.json"),
        lambda _: b'[{"exchange":"NSE"}]',
    )
    with pytest.raises(ValueError, match="missing or invalid Upstox instrument field"):
        source.fetch()


def test_http_source_requires_https():
    with pytest.raises(ValueError, match="HTTPS"):
        UpstoxInstrumentMasterConfig("http://example.test/bod.json")
