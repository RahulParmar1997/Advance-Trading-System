from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class InstrumentRecord:
    instrument: str
    exchange: str
    symbol: str
    asset_type: str
    trading_symbol: str | None = None
    is_active: bool = True

    def validate(self) -> None:
        if not self.instrument.strip():
            raise ValueError("instrument is required")
        if not self.exchange.strip():
            raise ValueError("exchange is required")
        if not self.symbol.strip():
            raise ValueError("symbol is required")
        if not self.asset_type.strip():
            raise ValueError("asset_type is required")


class InstrumentMaster:
    """Deterministic in-memory instrument registry; production storage stays injectable."""

    def __init__(self, records: Iterable[InstrumentRecord] = ()) -> None:
        self._records: dict[str, InstrumentRecord] = {}
        for record in records:
            self.upsert(record)

    def upsert(self, record: InstrumentRecord) -> None:
        record.validate()
        self._records[record.instrument] = record

    def get(self, instrument: str) -> InstrumentRecord:
        return self._records[instrument]

    def contains_active(self, instrument: str) -> bool:
        record = self._records.get(instrument)
        return record is not None and record.is_active

    def require_active(self, instrument: str) -> InstrumentRecord:
        record = self._records.get(instrument)
        if record is None:
            raise KeyError(f"unknown instrument: {instrument}")
        if not record.is_active:
            raise ValueError(f"inactive instrument: {instrument}")
        return record

    def __len__(self) -> int:
        return len(self._records)
