from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Sequence


@dataclass(frozen=True, slots=True)
class HistoricalOutcome:
    """One historical prediction paired with its realized binary outcome."""

    timestamp: datetime
    predicted_probability: Decimal
    outcome: bool

    def validate(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("historical outcome timestamp must be timezone-aware")
        if not Decimal("0") <= self.predicted_probability <= Decimal("1"):
            raise ValueError("predicted_probability must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class CalibrationBucket:
    lower: Decimal
    upper: Decimal
    observations: int
    positive_outcomes: int
    calibrated_probability: Decimal


@dataclass(frozen=True, slots=True)
class HistoricalCalibrationModel:
    """Empirical probability mapping learned only from pre-cutoff outcomes."""

    training_end: datetime
    buckets: tuple[CalibrationBucket, ...]
    bins: int

    def probability(self, predicted_probability: Decimal, *, observed_at: datetime) -> Decimal:
        if observed_at.tzinfo is None:
            raise ValueError("observation timestamp must be timezone-aware")
        if observed_at <= self.training_end:
            raise ValueError("calibration may only be applied out of sample")
        if not Decimal("0") <= predicted_probability <= Decimal("1"):
            raise ValueError("predicted_probability must be between 0 and 1")
        bucket = _find_bucket(self.buckets, predicted_probability, self.bins)
        if bucket is None:
            raise ValueError("no historical observations cover predicted probability")
        return bucket.calibrated_probability


class HistoricalProbabilityCalibrator:
    """Fit empirical probabilities from labeled history without future leakage."""

    def fit(
        self,
        samples: Sequence[HistoricalOutcome],
        *,
        training_end: datetime,
        bins: int = 10,
    ) -> HistoricalCalibrationModel:
        if training_end.tzinfo is None:
            raise ValueError("training_end must be timezone-aware")
        if bins <= 0:
            raise ValueError("bins must be positive")
        if not samples:
            raise ValueError("historical samples must not be empty")
        for sample in samples:
            sample.validate()
        training = [sample for sample in samples if sample.timestamp <= training_end]
        if not training:
            raise ValueError("no historical samples exist at or before training_end")
        width = Decimal("1") / Decimal(bins)
        buckets: list[CalibrationBucket] = []
        for index in range(bins):
            lower = width * Decimal(index)
            upper = Decimal("1") if index == bins - 1 else width * Decimal(index + 1)
            selected = [
                sample
                for sample in training
                if lower <= sample.predicted_probability < upper
                or (index == bins - 1 and sample.predicted_probability == upper)
            ]
            if not selected:
                continue
            positives = sum(1 for sample in selected if sample.outcome)
            buckets.append(
                CalibrationBucket(
                    lower=lower,
                    upper=upper,
                    observations=len(selected),
                    positive_outcomes=positives,
                    calibrated_probability=Decimal(positives) / Decimal(len(selected)),
                )
            )
        return HistoricalCalibrationModel(training_end, tuple(buckets), bins)


def _find_bucket(
    buckets: Sequence[CalibrationBucket],
    probability: Decimal,
    bins: int,
) -> CalibrationBucket | None:
    for bucket in buckets:
        if bucket.lower <= probability < bucket.upper or (
            bucket.upper == Decimal("1") and probability == bucket.upper
        ):
            return bucket
    return None
