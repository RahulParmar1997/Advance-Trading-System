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


def test_unmatched_rules_do_not_create_candidates():
    rule = ScannerRule("trend", AllOf((Condition(Field.REGIME, Operator.EQ, "TREND_UP"),)))
    assert ScannerPipeline().scan([rule], {"regime": "RANGE"}) == []
