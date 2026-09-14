from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping, Sequence

from advance_system.scanner.dsl import ScanResult, ScannerEngine, ScannerRule


@dataclass(frozen=True, slots=True)
class Candidate:
    candidate_id: str
    rule: str
    matched: bool
    evidence: tuple[str, ...]


class ScannerPipeline:
    """Cheap-first scanner pipeline with deterministic candidate identity."""

    def __init__(self, *, engine: ScannerEngine | None = None) -> None:
        self.engine = engine or ScannerEngine()

    @staticmethod
    def candidate_id(rule: ScannerRule, context: Mapping[str, object]) -> str:
        canonical = "|".join(f"{key}={context[key]!r}" for key in sorted(context))
        digest = sha256(f"{rule.name}|{canonical}".encode("utf-8")).hexdigest()
        return digest[:24]

    def scan(self, rules: Sequence[ScannerRule], context: Mapping[str, object]) -> list[Candidate]:
        # Rule order is explicit: callers should provide inexpensive gates first.
        # A failed rule does not prevent later independent rules from evaluating.
        seen: set[str] = set()
        candidates: list[Candidate] = []
        for rule in rules:
            result: ScanResult = self.engine.evaluate(rule, context)
            if not result.matched:
                continue
            candidate_id = self.candidate_id(rule, context)
            if candidate_id in seen:
                continue
            seen.add(candidate_id)
            candidates.append(Candidate(candidate_id, result.rule, True, result.reasons))
        return candidates
