from __future__ import annotations

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
