from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Iterable


@dataclass(frozen=True, slots=True)
class InstrumentMasterRecord:
    """Broker-neutral instrument identity used by market-data and execution layers."""

    instrument: str
    exchange: str
    symbol: str
    asset_type: str
    tradable: bool = True

    def validate(self) -> None:
        for field_name in ("instrument", "exchange", "symbol", "asset_type"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} is required")
        if self.exchange != self.exchange.upper():
            raise ValueError("exchange must be uppercase")
        if self.asset_type != self.asset_type.upper():
            raise ValueError("asset_type must be uppercase")

    def canonical_key(self) -> str:
        self.validate()
        return self.instrument.strip()


@dataclass(frozen=True, slots=True)
class InstrumentMasterSnapshot:
    """Immutable, content-addressed snapshot suitable for atomic publication."""

    version: int
    effective_at: datetime
    records: tuple[InstrumentMasterRecord, ...]
    checksum: str

    @classmethod
    def build(cls, records: Iterable[InstrumentMasterRecord], *, version: int, effective_at: datetime) -> "InstrumentMasterSnapshot":
        if version < 1:
            raise ValueError("version must be positive")
        if effective_at.tzinfo is None:
            raise ValueError("effective_at must be timezone-aware")
        ordered = tuple(sorted(records, key=lambda record: record.canonical_key()))
        if not ordered:
            raise ValueError("instrument master snapshot cannot be empty")
        keys: set[str] = set()
        payload: list[str] = []
        for record in ordered:
            record.validate()
            key = record.canonical_key()
            if key in keys:
                raise ValueError(f"duplicate instrument: {key}")
            keys.add(key)
            payload.append("|".join((key, record.exchange, record.symbol, record.asset_type, str(record.tradable))))
        checksum = sha256("\n".join(payload).encode("utf-8")).hexdigest()
        return cls(version=version, effective_at=effective_at, records=ordered, checksum=checksum)


class InstrumentMasterRepository:
    """Minimal atomic repository boundary; storage is injected by the application."""

    def __init__(self) -> None:
        self._current: InstrumentMasterSnapshot | None = None

    def current(self) -> InstrumentMasterSnapshot | None:
        return self._current

    def publish(self, snapshot: InstrumentMasterSnapshot) -> None:
        if self._current is not None and snapshot.version <= self._current.version:
            raise ValueError("snapshot version must increase")
        if snapshot.checksum != InstrumentMasterSnapshot.build(
            snapshot.records, version=snapshot.version, effective_at=snapshot.effective_at
        ).checksum:
            raise ValueError("snapshot checksum mismatch")
        self._current = snapshot
