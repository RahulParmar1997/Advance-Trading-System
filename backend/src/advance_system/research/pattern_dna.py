from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from math import sqrt
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class PatternDNA:
    """Immutable, normalized feature vector captured at decision time."""

    pattern_id: str
    features: tuple[tuple[str, Decimal], ...]
    outcome_r: Decimal | None = None

    @classmethod
    def from_mapping(
        cls,
        pattern_id: str,
        features: Mapping[str, Decimal],
        *,
        outcome_r: Decimal | None = None,
    ) -> "PatternDNA":
        if not pattern_id:
            raise ValueError("pattern_id is required")
        if not features:
            raise ValueError("features must not be empty")
        normalized = tuple(sorted((key, Decimal(value)) for key, value in features.items()))
        if any(not key for key, _ in normalized):
            raise ValueError("feature names must not be empty")
        return cls(pattern_id, normalized, outcome_r)

    def as_mapping(self) -> dict[str, Decimal]:
        return dict(self.features)


@dataclass(frozen=True, slots=True)
class SimilarPattern:
    pattern_id: str
    distance: Decimal
    outcome_r: Decimal | None


class PatternDNAEngine:
    """Deterministic Euclidean similarity search over explicit decision-time features."""

    def distance(self, left: PatternDNA, right: PatternDNA) -> Decimal:
        a = left.as_mapping()
        b = right.as_mapping()
        if set(a) != set(b):
            raise ValueError("patterns must have identical feature names")
        squared = sum((a[key] - b[key]) ** 2 for key in a)
        return Decimal(str(sqrt(float(squared))))

    def search(
        self,
        query: PatternDNA,
        corpus: Sequence[PatternDNA],
        *,
        limit: int = 5,
        max_distance: Decimal | None = None,
    ) -> tuple[SimilarPattern, ...]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        matches: list[SimilarPattern] = []
        for pattern in corpus:
            if pattern.pattern_id == query.pattern_id:
                continue
            distance = self.distance(query, pattern)
            if max_distance is not None and distance > max_distance:
                continue
            matches.append(SimilarPattern(pattern.pattern_id, distance, pattern.outcome_r))
        matches.sort(key=lambda item: (item.distance, item.pattern_id))
        return tuple(matches[:limit])

    def outcome_summary(self, matches: Sequence[SimilarPattern]) -> tuple[int, Decimal | None]:
        outcomes = [match.outcome_r for match in matches if match.outcome_r is not None]
        if not outcomes:
            return 0, None
        return len(outcomes), sum(outcomes, Decimal("0")) / Decimal(len(outcomes))
