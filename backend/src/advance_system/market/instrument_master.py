from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Iterable, Protocol

INSTRUMENT_MASTER_VERSION = 1


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


@dataclass(frozen=True, slots=True)
class InstrumentMasterSnapshot:
    version: int
    source: str
    as_of: datetime
    records: tuple[InstrumentRecord, ...]
    fingerprint: str

    @classmethod
    def build(cls, records: Iterable[InstrumentRecord], *, source: str, as_of: datetime) -> "InstrumentMasterSnapshot":
        if not source.strip():
            raise ValueError("instrument master source is required")
        if as_of.tzinfo is None:
            raise ValueError("instrument master timestamp must be timezone-aware")
        normalized = tuple(sorted(records, key=lambda r: (r.exchange.upper(), r.symbol.upper(), r.instrument)))
        seen: set[tuple[str, str]] = set()
        for record in normalized:
            record.validate()
            key = (record.exchange.upper(), record.symbol.upper())
            if key in seen:
                raise ValueError(f"duplicate instrument symbol: {record.exchange}:{record.symbol}")
            seen.add(key)
        payload = "\n".join(
            f"{r.instrument}|{r.exchange}|{r.symbol}|{r.asset_type}|{r.trading_symbol or ''}|{int(r.is_active)}"
            for r in normalized
        ).encode("utf-8")
        return cls(INSTRUMENT_MASTER_VERSION, source, as_of.astimezone(timezone.utc), normalized, sha256(payload).hexdigest())


class InstrumentMasterSource(Protocol):
    def load(self) -> Iterable[InstrumentRecord]: ...


class InstrumentMasterStore(Protocol):
    def current(self) -> InstrumentMasterSnapshot | None: ...
    def publish(self, snapshot: InstrumentMasterSnapshot) -> None: ...


class InMemoryInstrumentMasterStore:
    """Atomic snapshot store; a failed refresh cannot partially mutate the active registry."""

    def __init__(self) -> None:
        self._snapshot: InstrumentMasterSnapshot | None = None

    def current(self) -> InstrumentMasterSnapshot | None:
        return self._snapshot

    def publish(self, snapshot: InstrumentMasterSnapshot) -> None:
        current = self._snapshot
        if current is not None and snapshot.as_of < current.as_of:
            raise ValueError("instrument master timestamp cannot move backwards")
        self._snapshot = snapshot


class InstrumentMasterUpdater:
    """Builds a complete validated snapshot before publishing it."""

    def __init__(self, source: InstrumentMasterSource, store: InstrumentMasterStore) -> None:
        self._source = source
        self._store = store

    def refresh(self, *, source_name: str, as_of: datetime) -> InstrumentMasterSnapshot:
        snapshot = InstrumentMasterSnapshot.build(self._source.load(), source=source_name, as_of=as_of)
        current = self._store.current()
        if current is not None and current.fingerprint == snapshot.fingerprint:
            return current
        self._store.publish(snapshot)
        return snapshot


class InstrumentMaster:
    """Compatibility registry backed by the latest published snapshot."""

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
