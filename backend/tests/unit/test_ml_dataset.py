from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.research.ml_dataset import MLDatasetBuilder, ProbabilityCalibrator
from advance_system.research.pattern_dna import PatternDNA


def test_dataset_splits_chronologically_and_keeps_label_explicit() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    p1 = PatternDNA.from_mapping("p1", {"x": Decimal("1")}, outcome_r=Decimal("2"))
    p2 = PatternDNA.from_mapping("p2", {"x": Decimal("2")}, outcome_r=None)
    rows = MLDatasetBuilder().build([(p1, base), (p2, base + timedelta(days=2))], train_end=base, validation_end=base + timedelta(days=1))
    assert rows[0].split == "train"
    assert rows[0].label_r == Decimal("2")
    assert rows[1].split == "test"
    assert rows[1].label_r is None


def test_feature_matrix_rejects_schema_mismatch() -> None:
    builder = MLDatasetBuilder()
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    p1 = PatternDNA.from_mapping("p1", {"x": Decimal("1")})
    p2 = PatternDNA.from_mapping("p2", {"y": Decimal("2")})
    rows = builder.build([(p1, base), (p2, base)], train_end=base)
    with pytest.raises(ValueError):
        builder.feature_matrix(rows)


def test_calibration_uses_oos_predictions_and_boolean_outcomes() -> None:
    result = ProbabilityCalibrator().calibrate(
        [Decimal("0.1"), Decimal("0.2"), Decimal("0.9")],
        [False, True, True],
        bins=2,
    )
    assert len(result) == 2
    assert result[0].observations == 2
    assert result[0].observed_positive_rate == Decimal("0.5")
    assert result[1].observed_positive_rate == Decimal("1")


def test_calibration_rejects_invalid_probability() -> None:
    with pytest.raises(ValueError):
        ProbabilityCalibrator().calibrate([Decimal("1.1")], [True])
