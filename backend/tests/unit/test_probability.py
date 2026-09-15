from decimal import Decimal

import pytest

from advance_system.opportunity.engine import Opportunity
from advance_system.opportunity.probability import ProbabilityEVEngine


def opportunity(rr: str) -> Opportunity:
    return Opportunity(
        opportunity_id="opp-1",
        instrument="NSE_EQ|TEST",
        trade_type="BREAKOUT",
        strategy="breakout-continuation",
        strategy_version="1.0.0",
        direction="UP",
        entry=Decimal("100"),
        stop=Decimal("95"),
        target=Decimal(str(100 + 5 * Decimal(rr))),
        risk_reward=Decimal(rr),
        explanation=("structure confirmed",),
    )


def test_probability_is_bounded_and_ev_is_explicit():
    result = ProbabilityEVEngine().estimate(opportunity("2"))
    assert Decimal("0") <= result.estimated_win_probability <= Decimal("1")
    assert result.expected_value_r == Decimal("0.65")
    assert "empirical calibration" in result.evidence[0]


def test_invalid_prior_is_rejected():
    with pytest.raises(ValueError):
        ProbabilityEVEngine().estimate(opportunity("1"), base_probability=Decimal("1"))
