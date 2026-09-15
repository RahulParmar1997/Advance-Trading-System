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
        bucket = _find_bucket(self.buckets, predicted_probability)
        if bucket is None:
            raise ValueError("no historical observations cover predicted probability")
        return bucket.calibrated_probability


@dataclass(frozen=True, slots=True)
class CalibrationValidation:
    """Out-of-sample validation metrics; contains no fitted-model mutation."""

    observations: int
    brier_score: Decimal
    log_loss: Decimal
    accuracy: Decimal

    def validate(self) -> None:
        if self.observations <= 0:
            raise ValueError("validation observations must be positive")
        if not Decimal("0") <= self.brier_score <= Decimal("1"):
            raise ValueError("brier_score must be between 0 and 1")
        if self.log_loss < 0:
            raise ValueError("log_loss must be non-negative")
        if not Decimal("0") <= self.accuracy <= Decimal("1"):
            raise ValueError("accuracy must be between 0 and 1")


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

    def validate_oos(
        self,
        model: HistoricalCalibrationModel,
        samples: Sequence[HistoricalOutcome],
    ) -> CalibrationValidation:
        if not samples:
            raise ValueError("OOS validation samples must not be empty")
        for sample in samples:
            sample.validate()
            if sample.timestamp <= model.training_end:
                raise ValueError("OOS validation samples must be strictly after training_end")

        predictions: list[Decimal] = []
        outcomes: list[Decimal] = []
        correct = 0
        for sample in samples:
            calibrated = model.probability(sample.predicted_probability, observed_at=sample.timestamp)
            outcome = Decimal("1") if sample.outcome else Decimal("0")
            predictions.append(calibrated)
            outcomes.append(outcome)
            if (calibrated >= Decimal("0.5")) == sample.outcome:
                correct += 1

        brier = sum(
            ((prediction - outcome) ** 2 for prediction, outcome in zip(predictions, outcomes)),
            Decimal("0"),
        ) / Decimal(len(predictions))
        log_loss = sum(
            (_log_loss(prediction, outcome) for prediction, outcome in zip(predictions, outcomes)),
            Decimal("0"),
        ) / Decimal(len(predictions))
        result = CalibrationValidation(
            observations=len(predictions),
            brier_score=brier,
            log_loss=log_loss,
            accuracy=Decimal(correct) / Decimal(len(predictions)),
        )
        result.validate()
        return result


def _find_bucket(
    buckets: Sequence[CalibrationBucket],
    probability: Decimal,
) -> CalibrationBucket | None:
    for bucket in buckets:
        if bucket.lower <= probability < bucket.upper or (
            bucket.upper == Decimal("1") and probability == bucket.upper
        ):
            return bucket
    return None


def _log_loss(prediction: Decimal, outcome: Decimal) -> Decimal:
    """Compute log loss using Decimal-safe bounded probabilities."""
    from decimal import getcontext

    epsilon = Decimal("1e-12")
    bounded = min(max(prediction, epsilon), Decimal("1") - epsilon)
    if outcome == Decimal("1"):
        return -getcontext().ln(bounded)
    return -getcontext().ln(Decimal("1") - bounded)
