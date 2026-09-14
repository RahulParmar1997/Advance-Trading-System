from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime
from typing import Protocol

from advance_system.domain.instruments import InstrumentMasterRecord, InstrumentMasterRepository, InstrumentMasterSnapshot


class InstrumentMasterSource(Protocol):
    """Broker adapter boundary for downloading an instrument master."""

    async def fetch(self) -> Iterable[InstrumentMasterRecord]:
        ...


class InstrumentMasterUpdater:
    """Validate, version and atomically publish broker instrument-master snapshots."""

    def __init__(self, source: InstrumentMasterSource, repository: InstrumentMasterRepository) -> None:
        self._source = source
        self._repository = repository

    async def update(self, *, effective_at: datetime) -> InstrumentMasterSnapshot:
        current = self._repository.current()
        records = tuple(await self._source.fetch())
        next_version = 1 if current is None else current.version + 1
        snapshot = InstrumentMasterSnapshot.build(records, version=next_version, effective_at=effective_at)
        self._repository.publish(snapshot)
        return snapshot


class InstrumentMasterHttpClient(Protocol):
    """Minimal async HTTP boundary; transport, TLS and auth remain injectable."""

    async def get_text(self, url: str) -> str:
        ...


class UpstoxInstrumentMasterSource:
    """Parse an Upstox BOD JSON instrument file into broker-neutral records."""

    def __init__(self, client: InstrumentMasterHttpClient, url: str) -> None:
        if not url.strip():
            raise ValueError("instrument master url cannot be empty")
        self._client = client
        self._url = url

    async def fetch(self) -> tuple[InstrumentMasterRecord, ...]:
        payload = await self._client.get_text(self._url)
        return parse_upstox_instrument_master(payload)


def parse_upstox_instrument_master(payload: str) -> tuple[InstrumentMasterRecord, ...]:
    """Convert the documented Upstox JSON shape without trusting optional fields."""
    if not isinstance(payload, str) or not payload.strip():
        raise ValueError("instrument master payload must be non-empty text")
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid instrument master JSON") from exc
    if not isinstance(raw, list):
        raise ValueError("instrument master JSON must be an array")

    records: list[InstrumentMasterRecord] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"instrument master record {index} must be an object")
        required = ("instrument_key", "exchange", "trading_symbol", "instrument_type")
        missing = [field for field in required if not isinstance(item.get(field), str) or not item[field].strip()]
        if missing:
            raise ValueError(f"instrument master record {index} missing required fields: {', '.join(missing)}")
        segment = item.get("segment")
        asset_type = _map_upstox_asset_type(segment, item["instrument_type"])
        records.append(
            InstrumentMasterRecord(
                instrument=item["instrument_key"].strip(),
                exchange=item["exchange"].strip().upper(),
                symbol=item["trading_symbol"].strip(),
                asset_type=asset_type,
                tradable=True,
            )
        )
    return tuple(records)


def _map_upstox_asset_type(segment: object, instrument_type: str) -> str:
    """Map Upstox segment/type into the platform's stable uppercase asset taxonomy."""
    if not isinstance(segment, str) or not segment.strip():
        raise ValueError("instrument master record segment is required")
    segment = segment.strip().upper()
    instrument_type = instrument_type.strip().upper()
    if segment.endswith("_EQ") or instrument_type in {"EQ", "BE", "SM"}:
        return "EQUITY"
    if instrument_type == "INDEX" or segment.endswith("_INDEX"):
        return "INDEX"
    if instrument_type == "FUT":
        return "FUTURE"
    if instrument_type in {"CE", "PE"}:
        return "OPTION"
    if segment.endswith("_COM"):
        return "COMMODITY"
    if segment.endswith("_FO"):
        return "DERIVATIVE"
    return instrument_type
