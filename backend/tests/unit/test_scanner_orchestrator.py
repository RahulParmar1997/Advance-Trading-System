from datetime import datetime, timezone

import pytest

from advance_system.scanner.dsl import AllOf, Condition, Field, Operator, ScannerRule
from advance_system.scanner.orchestrator import ScanScope, ScannerOrchestrator


UTC = timezone.utc


def test_orchestrator_scans_multiple_symbols_and_timeframes_in_deterministic_order():
    rule = ScannerRule("trend", AllOf((Condition(Field.REGIME, Operator.EQ, "TREND_UP"),)))
    late = ScanScope("NIFTY", 900, datetime(2026, 9, 15, 10, 0, tzinfo=UTC))
    early = ScanScope("BANKNIFTY", 60, datetime(2026, 9, 15, 9, 30, tzinfo=UTC))
    scopes = [
        (late, {"regime": "TREND_UP"}),
        (early, {"regime": "TREND_UP"}),
    ]

    results = ScannerOrchestrator().scan(scopes, [rule])

    assert [(r.scope.instrument, r.scope.timeframe_seconds) for r in results] == [
        ("BANKNIFTY", 60),
        ("NIFTY", 900),
    ]
    assert all(r.candidate.result is not None for r in results)


def test_scope_context_mismatch_is_rejected():
    scope = ScanScope("NIFTY", 60, datetime(2026, 9, 15, 9, 30, tzinfo=UTC))
    with pytest.raises(ValueError, match="timeframe"):
        ScannerOrchestrator().scan([(scope, {"timeframe_seconds": 300})], [])


def test_scope_requires_timezone_aware_timestamp():
    scope = ScanScope("NIFTY", 60, datetime(2026, 9, 15, 9, 30))
    with pytest.raises(ValueError, match="timezone-aware"):
        ScannerOrchestrator().scan([(scope, {})], [])


def test_orchestrator_injects_scope_identity_into_result_context():
    rule = ScannerRule("trend", AllOf((Condition(Field.REGIME, Operator.EQ, "TREND_UP"),)))
    scope = ScanScope("NIFTY", 60, datetime(2026, 9, 15, 9, 30, tzinfo=UTC))
    result = ScannerOrchestrator().scan([(scope, {"regime": "TREND_UP"})], [rule])[0]

    assert result.candidate.result is not None
    assert result.candidate.result.instrument == "NIFTY"
    assert result.candidate.result.observed_at == scope.observed_at
