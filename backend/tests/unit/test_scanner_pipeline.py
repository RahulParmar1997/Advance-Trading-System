from datetime import datetime, timezone

from advance_system.scanner.dsl import AllOf, Condition, Field, Operator, ScannerRule
from advance_system.scanner.pipeline import ScannerPipeline


def test_pipeline_returns_stable_candidate_id_and_evidence():
    rule = ScannerRule("trend", AllOf((Condition(Field.REGIME, Operator.EQ, "TREND_UP"),)))
    context = {"regime": "TREND_UP", "structure_event": "BOS"}
    pipeline = ScannerPipeline()
    first = pipeline.scan([rule], context)
    second = pipeline.scan([rule], context)
    assert first == second
    assert len(first) == 1
    assert first[0].candidate_id
    assert first[0].evidence == ("regime eq TREND_UP",)


def test_pipeline_returns_rich_result_with_context_identity():
    rule = ScannerRule("trend", AllOf((Condition(Field.REGIME, Operator.EQ, "TREND_UP"),)))
    context = {
        "instrument": "NSE_EQ|TEST",
        "observed_at": datetime(2026, 1, 5, 10, 0, tzinfo=timezone.utc),
        "regime": "TREND_UP",
    }
    candidate = ScannerPipeline().scan([rule], context)[0]
    assert candidate.result is not None
    assert candidate.result.instrument == "NSE_EQ|TEST"
    assert candidate.result.observed_at == context["observed_at"]
    assert candidate.result.evidence[0].observed == "TREND_UP"
    assert candidate.result.explanation == "Rule 'trend' matched 1 explicit condition(s)."


def test_unmatched_rules_do_not_create_candidates():
    rule = ScannerRule("trend", AllOf((Condition(Field.REGIME, Operator.EQ, "TREND_UP"),)))
    assert ScannerPipeline().scan([rule], {"regime": "RANGE"}) == []
