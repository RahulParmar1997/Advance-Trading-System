from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.scanner.results import Evidence, ScannerResult
from advance_system.scanner.scoring import EvidenceScorer, EvidenceWeight

UTC = timezone.utc


def _result() -> ScannerResult:
    return ScannerResult(
        rule="trend-confirmation",
        matched=True,
        instrument="NIFTY",
        observed_at=datetime(2026, 9, 15, 10, 0, tzinfo=UTC),
        evidence=(
            Evidence("regime", "eq", "TREND_UP", "TREND_UP", True),
            Evidence("displacement", "eq", True, True, True),
            Evidence("volume_ratio", "gte", "1.5", Decimal("1.8"), False),
        ),
        explanation="explicit evidence",
    )


def test_scoring_is_deterministic_and_uses_only_matched_weighted_evidence():
    scorer = EvidenceScorer(
        [
            EvidenceWeight("volume_ratio", Decimal("2")),
            EvidenceWeight("regime", Decimal("3")),
            EvidenceWeight("displacement", Decimal("1")),
        ]
    )
    first = scorer.score(_result())
    second = scorer.score(_result())

    assert first == second
    assert first.score == Decimal("4")
    assert first.maximum_score == Decimal("6")
    assert first.matched_fields == ("displacement", "regime")
    assert "not a probability" in first.explanation


def test_duplicate_or_negative_weights_are_rejected():
    with pytest.raises(ValueError, match="unique"):
        EvidenceScorer([EvidenceWeight("regime", Decimal("1")), EvidenceWeight("regime", Decimal("2"))])
    with pytest.raises(ValueError, match="negative"):
        EvidenceScorer([EvidenceWeight("regime", Decimal("-1"))])


def test_score_cannot_be_created_from_invalid_scanner_result():
    result = ScannerResult("", True, None, None, (), "x")
    scorer = EvidenceScorer([EvidenceWeight("regime", Decimal("1"))])
    with pytest.raises(ValueError, match="rule"):
        scorer.score(result)
