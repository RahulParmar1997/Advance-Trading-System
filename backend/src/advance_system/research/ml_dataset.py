from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable, Sequence

from advance_system.research.pattern_dna import PatternDNA


@dataclass(frozen=True, slots=True)
class DatasetRow:
    pattern_id: str
    timestamp: datetime
    features: tuple[tuple[str, Decimal], ...]
    label_r: Decimal | None
    split: str

    @classmethod
    def from_pattern(cls, pattern: PatternDNA, timestamp: datetime, *, split: str) -> "DatasetRow":
        if timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        if split not in {"train", "validation", "test"}:
            raise ValueError("split must be train, validation or test")
        return cls(pattern.pattern_id, timestamp, pattern.features, pattern.outcome_r, split)


class MLDatasetBuilder:
    """Builds explicit feature/label rows while preventing outcome leakage."""

    def build(
        self,
        patterns: Sequence[tuple[PatternDNA, datetime]],
        *,
        train_end: datetime,
        validation_end: datetime | None = None,
    ) -> tuple[DatasetRow, ...]:
        if train_end.tzinfo is None or (validation_end is not None and validation_end.tzinfo is None):
            raise ValueError("split boundaries must be timezone-aware")
        if validation_end is not None and validation_end <= train_end:
            raise ValueError("validation_end must be after train_end")
        rows: list[DatasetRow] = []
        for pattern, timestamp in patterns:
            if timestamp.tzinfo is None:
                raise ValueError("row timestamp must be timezone-aware")
            if timestamp <= train_end:
                split = "train"
            elif validation_end is None or timestamp <= validation_end:
                split = "validation"
            else:
                split = "test"
            rows.append(DatasetRow.from_pattern(pattern, timestamp, split=split))
        rows.sort(key=lambda row: (row.timestamp, row.pattern_id))
        return tuple(rows)

    def training_rows(self, rows: Iterable[DatasetRow]) -> tuple[DatasetRow, ...]:
        return tuple(row for row in rows if row.split == "train")

    def feature_matrix(self, rows: Sequence[DatasetRow]) -> tuple[tuple[Decimal, ...], tuple[str, ...]]:
        if not rows:
            return (), ()
        names = tuple(name for name, _ in rows[0].features)
        if any(tuple(name for name, _ in row.features) != names for row in rows):
            raise ValueError("all dataset rows must have identical feature schemas")
        return tuple(tuple(value for _, value in row.features) for row in rows), names


@dataclass(frozen=True, slots=True)
class CalibrationBin:
    lower: Decimal
    upper: Decimal
    observations: int
    mean_predicted: Decimal
    observed_positive_rate: Decimal


class ProbabilityCalibrator:
    """Simple deterministic reliability bins over explicit OOS predictions."""

    def calibrate(
        self,
        predictions: Sequence[Decimal],
        outcomes: Sequence[bool],
        *,
        bins: int = 10,
    ) -> tuple[CalibrationBin, ...]:
        if len(predictions) != len(outcomes) or not predictions:
            raise ValueError("predictions and outcomes must have equal non-zero length")
        if bins <= 0:
            raise ValueError("bins must be positive")
        if any(not Decimal("0") <= p <= Decimal("1") for p in predictions):
            raise ValueError("predictions must be between 0 and 1")
        result: list[CalibrationBin] = []
        width = Decimal("1") / Decimal(bins)
        for index in range(bins):
            lower = width * Decimal(index)
            upper = Decimal("1") if index == bins - 1 else width * Decimal(index + 1)
            selected = [i for i, p in enumerate(predictions) if lower <= p < upper or (index == bins - 1 and p == upper)]
            if not selected:
                continue
            result.append(CalibrationBin(
                lower,
                upper,
                len(selected),
                sum((predictions[i] for i in selected), Decimal("0")) / Decimal(len(selected)),
                Decimal(sum(1 for i in selected if outcomes[i])) / Decimal(len(selected)),
            ))
        return tuple(result)
