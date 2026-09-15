from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.scanner.dsl import AllOf, Condition, Field, Operator, ScannerEngine, ScannerRule
from advance_system.scanner.results import Evidence, build_scanner_result


def test_build_scanner_result_exposes_explicit_evidence_and_explanation() -> None:
    rule = ScannerRule(
        "trend-confirmed",
        AllOf(
            (
                Condition(Field.REGIME, Operator.EQ, "TREND_UP"),
                Condition(Field.LIQUIDITY_DISTANCE, Operator.LTE, Decimal("1.5")),
            )
        ),
    )
    context = {
        "instrument": "NSE_EQ|TEST",
        "observed_at": datetime(2026, 1, 5, 10, 0, tzinfo=timezone.utc),
        "regime": "TREND_UP",
        "liquidity_distance": Decimal("1.25"),
    }
    result = build_scanner_result(ScannerEngine().evaluate(rule, context), context)
    assert result.matched
    assert result.instrument == "NSE_EQ|TEST"
    assert len(result.evidence) == 2
    assert result.evidence[0].field == "regime"
    assert result.evidence[0].observed == "TREND_UP"
    assert "trend-confirmed" in result.explanation


def test_unmatched_result_is_explicit_and_has_no_fake_evidence() -> None:
    rule = ScannerRule("trend", AllOf((Condition(Field.REGIME, Operator.EQ, "TREND_UP"),)))
    result = build_scanner_result(ScannerEngine().evaluate(rule, {"regime": "RANGE"}), {"regime": "RANGE"})
    assert not result.matched
    assert result.evidence == ()
    assert "did not match" in result.explanation


def test_result_rejects_naive_observation_time() -> None:
    evidence = Evidence("regime", "eq", "TREND_UP", "TREND_UP", True)
    from advance_system.scanner.results import ScannerResult

    result = ScannerResult("trend", True, None, datetime(2026, 1, 5, 10, 0), (evidence,), "matched")
    with pytest.raises(ValueError, match="timezone-aware"):
        result.validate()


def test_result_never_introduces_probability_or_risk_fields() -> None:
    rule = ScannerRule("trend", AllOf((Condition(Field.REGIME, Operator.EQ, "TREND_UP"),)))
    result = build_scanner_result(ScannerEngine().evaluate(rule, {"regime": "TREND_UP"}), {"regime": "TREND_UP"})
    assert not hasattr(result, "probability")
    assert not hasattr(result, "risk_decision")
