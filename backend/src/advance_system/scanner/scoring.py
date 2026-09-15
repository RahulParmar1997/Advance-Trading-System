from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping, Sequence

from advance_system.scanner.results import Evidence, ScannerResult


@dataclass(frozen=True, slots=True)
class EvidenceWeight:
    field: str
    weight: Decimal

    def validate(self) -> None:
        if not self.field.strip():
            raise ValueError("evidence weight field is required")
        if self.weight < 0:
            raise ValueError("evidence weight cannot be negative")


@dataclass(frozen=True, slots=True)
class ScoreResult:
    rule: str
    score: Decimal
    maximum_score: Decimal
    matched_fields: tuple[str, ...]
    explanation: str

    def validate(self) -> None:
        if not self.rule.strip():
            raise ValueError("score rule is required")
        if self.score < 0 or self.maximum_score < 0 or self.score > self.maximum_score:
            raise ValueError("score must be between zero and maximum_score")
        if not self.explanation.strip():
            raise ValueError("score explanation is required")


class EvidenceScorer:
    """Deterministic weighted evidence scorer; not a probability model."""

    def __init__(self, weights: Sequence[EvidenceWeight]) -> None:
        normalized = tuple(weights)
        if not normalized:
            raise ValueError("at least one evidence weight is required")
        for weight in normalized:
            weight.validate()
        fields = [weight.field for weight in normalized]
        if len(set(fields)) != len(fields):
            raise ValueError("evidence weight fields must be unique")
        self._weights = tuple(sorted(normalized, key=lambda item: item.field))

    def score(self, result: ScannerResult) -> ScoreResult:
        result.validate()
        weights: Mapping[str, Decimal] = {item.field: item.weight for item in self._weights}
        maximum = sum(weights.values(), Decimal("0"))
        score = Decimal("0")
        matched_fields: list[str] = []
        for evidence in result.evidence:
            if evidence.matched and evidence.field in weights:
                score += weights[evidence.field]
                matched_fields.append(evidence.field)
        matched_fields = sorted(set(matched_fields))
        explanation = (
            f"Rule '{result.rule}' scored {score} of {maximum} from explicit evidence. "
            "This score is not a probability or expected value."
        )
        output = ScoreResult(result.rule, score, maximum, tuple(matched_fields), explanation)
        output.validate()
        return output
