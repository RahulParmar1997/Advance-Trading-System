from decimal import Decimal

import pytest

from advance_system.opportunity.engine import OpportunityEngine


def test_builds_up_opportunity_and_calculates_risk_reward():
    opportunity = OpportunityEngine().build(
        opportunity_id="cand-1",
        instrument="NSE_EQ|TEST",
        trade_type="BREAKOUT",
        strategy="breakout-continuation",
        strategy_version="1.0.0",
        direction="UP",
        entry=Decimal("100"),
        stop=Decimal("98"),
        target=Decimal("106"),
        explanation=("BOS confirmed", "FVG aligned"),
    )
    assert opportunity.risk_reward == Decimal("3")
    assert opportunity.explanation == ("BOS confirmed", "FVG aligned")


def test_builds_down_opportunity_with_correct_risk_reward():
    opportunity = OpportunityEngine().build(
        opportunity_id="cand-2",
        instrument="NSE_EQ|TEST",
        trade_type="BREAKOUT",
        strategy="breakout-continuation",
        strategy_version="1.0.0",
        direction="DOWN",
        entry=Decimal("100"),
        stop=Decimal("103"),
        target=Decimal("94"),
    )
    assert opportunity.risk_reward == Decimal("2")


def test_invalid_price_geometry_is_rejected():
    with pytest.raises(ValueError):
        OpportunityEngine().build(
            opportunity_id="bad",
            instrument="NSE_EQ|TEST",
            trade_type="BREAKOUT",
            strategy="breakout-continuation",
            strategy_version="1.0.0",
            direction="UP",
            entry=Decimal("100"),
            stop=Decimal("101"),
            target=Decimal("106"),
        )
