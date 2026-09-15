from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Sequence

from advance_system.scanner.dsl import ScannerRule
from advance_system.scanner.pipeline import Candidate, ScannerPipeline


@dataclass(frozen=True, slots=True, order=True)
class ScanScope:
    """Explicit scanner identity for one instrument/timeframe observation."""

    instrument: str
    timeframe_seconds: int
    observed_at: datetime

    def validate(self) -> None:
        if not self.instrument.strip():
            raise ValueError("scan scope instrument is required")
        if self.timeframe_seconds <= 0:
            raise ValueError("scan scope timeframe_seconds must be positive")
        if self.observed_at.tzinfo is None:
            raise ValueError("scan scope observed_at must be timezone-aware")


@dataclass(frozen=True, slots=True)
class ScopedCandidate:
    scope: ScanScope
    candidate: Candidate


class ScannerOrchestrator:
    """Deterministic multi-symbol/multi-timeframe scanner coordinator."""

    def __init__(self, *, pipeline: ScannerPipeline | None = None) -> None:
        self.pipeline = pipeline or ScannerPipeline()

    def scan(
        self,
        scopes: Sequence[tuple[ScanScope, Mapping[str, object]]],
        rules: Sequence[ScannerRule],
    ) -> list[ScopedCandidate]:
        normalized: list[tuple[ScanScope, Mapping[str, object]]] = []
        for scope, context in scopes:
            scope.validate()
            context_instrument = context.get("instrument")
            context_timeframe = context.get("timeframe_seconds")
            context_observed_at = context.get("observed_at")
            if context_instrument is not None and context_instrument != scope.instrument:
                raise ValueError("scanner context instrument does not match scope")
            if context_timeframe is not None and context_timeframe != scope.timeframe_seconds:
                raise ValueError("scanner context timeframe does not match scope")
            if context_observed_at is not None and context_observed_at != scope.observed_at:
                raise ValueError("scanner context observed_at does not match scope")
            enriched = dict(context)
            enriched.setdefault("instrument", scope.instrument)
            enriched.setdefault("timeframe_seconds", scope.timeframe_seconds)
            enriched.setdefault("observed_at", scope.observed_at)
            normalized.append((scope, enriched))

        normalized.sort(key=lambda item: item[0])
        results: list[ScopedCandidate] = []
        for scope, context in normalized:
            for candidate in self.pipeline.scan(rules, context):
                results.append(ScopedCandidate(scope, candidate))
        return results
