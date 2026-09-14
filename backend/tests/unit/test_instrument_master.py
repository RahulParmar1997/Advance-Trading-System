from datetime import datetime, timezone

import pytest

from advance_system.domain.instruments import InstrumentMasterRecord, InstrumentMasterRepository, InstrumentMasterSnapshot
from advance_system.ingestion.instrument_master import InstrumentMasterUpdater


class FakeSource:
    def __init__(self, records):
        self.records = records

    async def fetch(self):
        return self.records


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
