from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping, Sequence

from advance_system.scanner.dsl import ScannerEngine, ScannerRule, ScanResult
from advance_system.scanner.results import ScannerResult, build_scanner_result


@dataclass(frozen=True, slots=True)
class Candidate:
    candidate_id: str
    rule: str
    matched: bool
    evidence: tuple[str, ...]
    result: ScannerResult | None = None


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
        seen: set[str] = set()
        candidates: list[Candidate] = []
        for rule in rules:
            raw: ScanResult = self.engine.evaluate(rule, context)
            if not raw.matched:
                continue
            candidate_id = self.candidate_id(rule, context)
            if candidate_id in seen:
                continue
            seen.add(candidate_id)
            result = build_scanner_result(raw, context)
            candidates.append(Candidate(candidate_id, raw.rule, True, raw.reasons, result))
        return candidates
