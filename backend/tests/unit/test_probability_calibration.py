from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.research.calibration import HistoricalOutcome, HistoricalProbabilityCalibrator

UTC = timezone.utc


def test_fit_uses_only_history_and_applies_empirical_rate_out_of_sample():
    base = datetime(2026, 1, 1, tzinfo=UTC)
    samples = (
        HistoricalOutcome(base, Decimal("0.10"), False),
        HistoricalOutcome(base + timedelta(days=1), Decimal("0.20"), True),
        HistoricalOutcome(base + timedelta(days=2), Decimal("0.80"), True),
        HistoricalOutcome(base + timedelta(days=3), Decimal("0.90"), False),
        HistoricalOutcome(base + timedelta(days=10), Decimal("0.10"), True),
    )
    model = HistoricalProbabilityCalibrator().fit(samples, training_end=base + timedelta(days=3), bins=2)

    assert model.probability(Decimal("0.15"), observed_at=base + timedelta(days=4)) == Decimal("0.5")
    assert model.probability(Decimal("0.85"), observed_at=base + timedelta(days=4)) == Decimal("0.5")


def test_calibration_rejects_in_sample_application():
    base = datetime(2026, 1, 1, tzinfo=UTC)
    model = HistoricalProbabilityCalibrator().fit(
        [HistoricalOutcome(base, Decimal("0.2"), True)],
        training_end=base,
        bins=2,
    )
    with pytest.raises(ValueError, match="out of sample"):
        model.probability(Decimal("0.2"), observed_at=base)


def test_calibration_does_not_use_future_outcomes_when_fitting():
    base = datetime(2026, 1, 1, tzinfo=UTC)
    model = HistoricalProbabilityCalibrator().fit(
        [
            HistoricalOutcome(base, Decimal("0.2"), False),
            HistoricalOutcome(base + timedelta(days=1), Decimal("0.2"), True),
        ],
        training_end=base,
        bins=2,
    )
    assert model.probability(Decimal("0.2"), observed_at=base + timedelta(days=2)) == Decimal("0")


def test_calibration_rejects_uncovered_probability_and_invalid_input():
    base = datetime(2026, 1, 1, tzinfo=UTC)
    model = HistoricalProbabilityCalibrator().fit(
        [HistoricalOutcome(base, Decimal("0.2"), True)],
        training_end=base,
        bins=2,
    )
    with pytest.raises(ValueError, match="no historical observations"):
        model.probability(Decimal("0.8"), observed_at=base + timedelta(days=1))
    with pytest.raises(ValueError):
        HistoricalProbabilityCalibrator().fit(
            [HistoricalOutcome(base, Decimal("1.2"), True)],
            training_end=base,
        )


def test_oos_validation_calculates_brier_log_loss_and_accuracy():
    base = datetime(2026, 1, 1, tzinfo=UTC)
    calibrator = HistoricalProbabilityCalibrator()
    model = calibrator.fit(
        [
            HistoricalOutcome(base, Decimal("0.2"), True),
            HistoricalOutcome(base, Decimal("0.8"), False),
        ],
        training_end=base,
        bins=2,
    )
    result = calibrator.validate_oos(
        model,
        [
            HistoricalOutcome(base + timedelta(days=1), Decimal("0.2"), True),
            HistoricalOutcome(base + timedelta(days=2), Decimal("0.8"), False),
        ],
    )
    assert result.observations == 2
    assert result.brier_score == Decimal("0")
    assert result.log_loss == Decimal("0")
    assert result.accuracy == Decimal("1")


def test_oos_validation_rejects_training_period_and_does_not_mutate_model():
    base = datetime(2026, 1, 1, tzinfo=UTC)
    calibrator = HistoricalProbabilityCalibrator()
    model = calibrator.fit(
        [HistoricalOutcome(base, Decimal("0.2"), True)],
        training_end=base,
        bins=2,
    )
    before = model
    with pytest.raises(ValueError, match="strictly after"):
        calibrator.validate_oos(model, [HistoricalOutcome(base, Decimal("0.2"), True)])
    assert model == before
