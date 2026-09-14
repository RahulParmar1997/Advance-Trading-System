from decimal import Decimal

from advance_system.scanner.dsl import AllOf, Condition, Field, Operator, ScannerEngine, ScannerRule


def test_scanner_rule_is_typed_and_deterministic():
    rule = ScannerRule(
        "trend-bos-fvg",
        AllOf(
            (
                Condition(Field.REGIME, Operator.EQ, "TREND_UP"),
                Condition(Field.STRUCTURE_EVENT, Operator.EQ, "BOS"),
                Condition(Field.FVG_DIRECTION, Operator.EQ, "UP"),
                Condition(Field.LIQUIDITY_DISTANCE, Operator.LTE, Decimal("1.5")),
                Condition(Field.VOLUME_CONFIRMATION, Operator.EQ, True),
            )
        ),
    )
    context = {
        "regime": "TREND_UP",
        "structure_event": "BOS",
        "fvg_direction": "UP",
        "liquidity_distance": Decimal("1.25"),
        "volume_confirmation": True,
    }
    result = ScannerEngine().evaluate(rule, context)
    assert result.matched
    assert len(result.reasons) == 5


def test_missing_context_field_cannot_match():
    rule = ScannerRule("requires-regime", AllOf((Condition(Field.REGIME, Operator.EQ, "TREND_UP"),)))
    result = ScannerEngine().evaluate(rule, {})
    assert not result.matched
    assert result.reasons == ()
