from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from advance_system.opportunity.engine import Opportunity


@dataclass(frozen=True, slots=True)
class ProbabilityEstimate:
    opportunity_id: str
    estimated_win_probability: Decimal
    expected_value_r: Decimal
    method: str
    evidence: tuple[str, ...]

    def validate(self) -> None:
        if not Decimal("0") <= self.estimated_win_probability <= Decimal("1"):
            raise ValueError("estimated_win_probability must be between 0 and 1")


class ProbabilityEVEngine:
    """Deterministic baseline estimate; not a claim of predictive accuracy."""

    def estimate(self, opportunity: Opportunity, *, base_probability: Decimal = Decimal("0.5")) -> ProbabilityEstimate:
        if not Decimal("0") < base_probability < Decimal("1"):
            raise ValueError("base_probability must be between 0 and 1")
        probability = base_probability
        evidence = ["baseline prior; requires empirical calibration"]
        if opportunity.risk_reward >= Decimal("2"):
            probability = min(Decimal("0.7"), probability + Decimal("0.05"))
            evidence.append("risk-reward >= 2")
        expected_value = probability * opportunity.risk_reward - (Decimal("1") - probability)
        estimate = ProbabilityEstimate(opportunity.opportunity_id, probability, expected_value, "baseline-r:r-v1", tuple(evidence))
        estimate.validate()
        return estimate
