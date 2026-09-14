from datetime import datetime, timezone

import pytest

from advance_system.domain.instruments import InstrumentMasterRecord, InstrumentMasterRepository, InstrumentMasterSnapshot
from advance_system.ingestion.instrument_master import (
    InstrumentMasterUpdater,
    UpstoxInstrumentMasterSource,
    parse_upstox_instrument_master,
)


class FakeSource:
    def __init__(self, records):
        self.records = records

    async def fetch(self):
        return self.records


class FakeHttpClient:
    def __init__(self, payload):
        self.payload = payload
        self.urls = []

    async def get_text(self, url):
        self.urls.append(url)
        return self.payload


def record(symbol="RELIANCE"):
    return InstrumentMasterRecord(
        instrument=f"NSE_EQ|{symbol}", exchange="NSE", symbol=symbol, asset_type="EQUITY"
    )


def test_snapshot_is_sorted_and_content_addressed():
    snapshot = InstrumentMasterSnapshot.build(
        [record("TCS"), record("RELIANCE")], version=1, effective_at=datetime.now(timezone.utc)
    )
    assert [item.symbol for item in snapshot.records] == ["RELIANCE", "TCS"]
    assert len(snapshot.checksum) == 64


def test_snapshot_rejects_duplicates_and_invalid_records():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="duplicate instrument"):
        InstrumentMasterSnapshot.build([record(), record()], version=1, effective_at=now)
    with pytest.raises(ValueError, match="exchange must be uppercase"):
        InstrumentMasterSnapshot.build(
            [InstrumentMasterRecord("x", "nse", "X", "EQUITY")], version=1, effective_at=now
        )


@pytest.mark.asyncio
async def test_updater_publishes_monotonically_versioned_snapshot():
    repository = InstrumentMasterRepository()
    updater = InstrumentMasterUpdater(FakeSource([record()]), repository)
    first = await updater.update(effective_at=datetime.now(timezone.utc))
    second = await updater.update(effective_at=datetime.now(timezone.utc))
    assert first.version == 1
    assert second.version == 2
    assert repository.current() == second


@pytest.mark.asyncio
async def test_invalid_source_data_does_not_replace_current_snapshot():
    repository = InstrumentMasterRepository()
    valid = InstrumentMasterUpdater(FakeSource([record()]), repository)
    first = await valid.update(effective_at=datetime.now(timezone.utc))

    invalid = InstrumentMasterUpdater(FakeSource([]), repository)
    with pytest.raises(ValueError, match="cannot be empty"):
        await invalid.update(effective_at=datetime.now(timezone.utc))
    assert repository.current() == first


def test_upstox_json_parser_maps_documented_instrument_types():
    payload = """
    [
      {"segment":"NSE_EQ","exchange":"NSE","instrument_key":"NSE_EQ|INE002A01018","trading_symbol":"RELIANCE","instrument_type":"EQ"},
      {"segment":"NSE_INDEX","exchange":"NSE","instrument_key":"NSE_INDEX|Nifty 50","trading_symbol":"NIFTY","instrument_type":"INDEX"},
      {"segment":"NSE_FO","exchange":"NSE","instrument_key":"NSE_FO|123","trading_symbol":"RELIANCE FUT","instrument_type":"FUT"},
      {"segment":"NSE_FO","exchange":"NSE","instrument_key":"NSE_FO|124","trading_symbol":"RELIANCE CE","instrument_type":"CE"}
    ]
    """
    records = parse_upstox_instrument_master(payload)
    assert [(r.instrument, r.asset_type) for r in records] == [
        ("NSE_EQ|INE002A01018", "EQUITY"),
        ("NSE_INDEX|Nifty 50", "INDEX"),
        ("NSE_FO|123", "FUTURE"),
        ("NSE_FO|124", "OPTION"),
    ]


def test_upstox_json_parser_fails_closed_on_malformed_input():
    with pytest.raises(ValueError, match="invalid instrument master JSON"):
        parse_upstox_instrument_master("not-json")
    with pytest.raises(ValueError, match="must be an array"):
        parse_upstox_instrument_master("{}")
    with pytest.raises(ValueError, match="missing required fields"):
        parse_upstox_instrument_master('[{"segment":"NSE_EQ"}]')


@pytest.mark.asyncio
async def test_upstox_source_uses_injected_http_client():
    client = FakeHttpClient('[{"segment":"NSE_EQ","exchange":"NSE","instrument_key":"NSE_EQ|ABC","trading_symbol":"ABC","instrument_type":"EQ"}]')
    source = UpstoxInstrumentMasterSource(client, "https://example.test/instruments.json")
    records = await source.fetch()
    assert client.urls == ["https://example.test/instruments.json"]
    assert records[0].instrument == "NSE_EQ|ABC"
