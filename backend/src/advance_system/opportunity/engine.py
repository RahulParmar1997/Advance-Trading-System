from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from advance_system.domain.versioning import ContractName, validate_contract_version


@dataclass(frozen=True, slots=True)
class Opportunity:
    opportunity_id: str
    instrument: str
    trade_type: str
    strategy: str
    strategy_version: str
    direction: str
    entry: Decimal
    stop: Decimal
    target: Decimal
    risk_reward: Decimal
    explanation: tuple[str, ...]
    contract_version: int = 1

    def validate(self) -> None:
        validate_contract_version(ContractName.OPPORTUNITY, self.contract_version)
        if not self.opportunity_id or not self.instrument:
            raise ValueError("opportunity_id and instrument are required")
        if self.entry <= 0 or self.stop <= 0 or self.target <= 0:
            raise ValueError("entry, stop and target must be positive")
        if self.direction not in {"UP", "DOWN"}:
            raise ValueError("direction must be UP or DOWN")
        if self.direction == "UP" and not (self.stop < self.entry < self.target):
            raise ValueError("UP opportunity requires stop < entry < target")
        if self.direction == "DOWN" and not (self.target < self.entry < self.stop):
            raise ValueError("DOWN opportunity requires target < entry < stop")
        if self.risk_reward <= 0:
            raise ValueError("risk_reward must be positive")


class OpportunityEngine:
    """Builds trade opportunities without probability, risk approval, or order submission."""

    def build(
        self,
        *,
        opportunity_id: str,
        instrument: str,
        trade_type: str,
        strategy: str,
        strategy_version: str,
        direction: str,
        entry: Decimal,
        stop: Decimal,
        target: Decimal,
        explanation: tuple[str, ...] = (),
        contract_version: int = 1,
    ) -> Opportunity:
        if direction == "UP":
            risk = entry - stop
            reward = target - entry
        elif direction == "DOWN":
            risk = stop - entry
            reward = entry - target
        else:
            raise ValueError("direction must be UP or DOWN")
        if risk <= 0 or reward <= 0:
            raise ValueError("entry/stop/target do not define positive risk and reward")
        opportunity = Opportunity(
            opportunity_id=opportunity_id,
            instrument=instrument,
            trade_type=trade_type,
            strategy=strategy,
            strategy_version=strategy_version,
            direction=direction,
            entry=entry,
            stop=stop,
            target=target,
            risk_reward=reward / risk,
            explanation=explanation,
            contract_version=contract_version,
        )
        opportunity.validate()
        return opportunity
