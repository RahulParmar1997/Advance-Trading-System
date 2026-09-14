from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from advance_system.domain.instruments import InstrumentMasterRecord


@dataclass(frozen=True, slots=True)
class UpstoxInstrumentMasterConfig:
    """Configuration for the official Upstox BOD JSON instrument source."""

    url: str

    def __post_init__(self) -> None:
        if not self.url.startswith("https://"):
            raise ValueError("instrument master URL must use HTTPS")


class UpstoxInstrumentMasterSource:
    """Parse an Upstox BOD JSON payload into broker-neutral records.

    HTTP transport is injected so production networking, retries and credentials remain
    outside the parser and are independently testable.
    """

    def __init__(self, config: UpstoxInstrumentMasterConfig, fetch_bytes: Callable[[str], bytes]) -> None:
        self._config = config
        self._fetch_bytes = fetch_bytes

    def fetch(self) -> Iterable[InstrumentMasterRecord]:
        payload = self._fetch_bytes(self._config.url)
        try:
            decoded: Any = json.loads(payload)
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid Upstox instrument master JSON") from exc
        if not isinstance(decoded, list):
            raise ValueError("Upstox instrument master payload must be a JSON array")
        return tuple(self._parse_record(item) for item in decoded)

    @staticmethod
    def _parse_record(item: Any) -> InstrumentMasterRecord:
        if not isinstance(item, dict):
            raise ValueError("Upstox instrument record must be an object")
        try:
            return InstrumentMasterRecord(
                instrument=str(item["instrument_key"]),
                exchange=str(item["exchange"]),
                symbol=str(item.get("trading_symbol") or item["symbol"]),
                asset_type=str(item.get("instrument_type") or item["segment"]),
                tradable=True,
            )
        except KeyError as exc:
            raise ValueError(f"missing Upstox instrument field: {exc.args[0]}") from exc
