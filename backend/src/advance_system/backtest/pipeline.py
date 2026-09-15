from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Mapping

from advance_system.backtest.engine import BacktestEvent, BacktestFill, EventDrivenBacktester
from advance_system.domain.market_status import MarketStatus
from advance_system.oms.state_machine import OmsOrder, OmsState, OrderStateMachine
from advance_system.opportunity.engine import Opportunity, OpportunityEngine
from advance_system.risk.engine import RiskContext, RiskEngine, RiskSnapshot
from advance_system.strategy.engine import Strategy, StrategyContext


@dataclass(frozen=True, slots=True)
class BacktestDecision:
    timestamp: datetime
    opportunity: Opportunity | None
    risk_allowed: bool
    risk_reason: str
    oms_state: OmsState


@dataclass(frozen=True, slots=True)
class IntegratedBacktestResult:
    fills: tuple[BacktestFill, ...]
    decisions: tuple[BacktestDecision, ...]


class IntegratedBacktestPipeline:
    """Historical decision pipeline using the same Strategy, RiskEngine and OMS contracts."""

    def __init__(self, strategy: Strategy, risk_engine: RiskEngine) -> None:
        self._strategy = strategy
        self._risk = risk_engine
        self._opportunity = OpportunityEngine()
        self._oms = OrderStateMachine()
        self._execution = EventDrivenBacktester()

    def run(
        self,
        events: list[BacktestEvent],
        *,
        trade_type: str,
        stop: Decimal,
        target: Decimal,
        quantity: int,
        starting_cash: Decimal,
        market_open: bool = True,
        probability: Decimal | None = None,
        market_context: Mapping[str, object] | None = None,
        market_status: MarketStatus | None = None,
    ) -> IntegratedBacktestResult:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        ordered = sorted(events, key=lambda event: event.timestamp)
        decisions: list[BacktestDecision] = []
        approved_events: list[BacktestEvent] = []

        for event in ordered:
            context = StrategyContext(event.instrument, trade_type, market_context or {})
            decision = self._strategy.evaluate(context)
            if not decision.eligible or decision.direction is None:
                decisions.append(BacktestDecision(event.timestamp, None, False, decision.reason, OmsState.REJECTED))
                continue

            opportunity = self._opportunity.build(
                opportunity_id=f"bt:{event.instrument}:{event.timestamp.isoformat()}:{decision.strategy}:{decision.version}",
                instrument=event.instrument,
                trade_type=trade_type,
                strategy=decision.strategy,
                strategy_version=decision.version,
                direction=decision.direction,
                entry=event.price,
                stop=stop,
                target=target,
                explanation=(decision.reason,),
            )
            snapshot = RiskSnapshot(available_liquidity=starting_cash)
            estimated_market_volume = Decimal("0")
            if event.liquidity is not None and event.liquidity.market_volume is not None:
                estimated_market_volume = event.price * Decimal(event.liquidity.market_volume)
            risk_context = RiskContext(
                now=event.timestamp,
                market_open=market_open,
                last_market_data_at=event.timestamp,
                snapshot=snapshot,
                probability=probability,
                order_notional=event.price * quantity,
                estimated_market_volume=estimated_market_volume,
                market_status=market_status,
                expected_exchange=market_status.exchange if market_status is not None else None,
            )
            risk = self._risk.check(opportunity, risk_context)
            if not risk.allowed:
                decisions.append(BacktestDecision(event.timestamp, opportunity, False, risk.reason, OmsState.REJECTED))
                continue

            order = OmsOrder(
                order_id=opportunity.opportunity_id,
                instrument=event.instrument,
                quantity=quantity,
            )
            for state in (OmsState.CANDIDATE, OmsState.QUALIFIED, OmsState.RISK_CHECK, OmsState.ORDER_PENDING):
                order = self._oms.transition(order, state)
            decisions.append(BacktestDecision(event.timestamp, opportunity, True, risk.reason, order.state))
            approved_events.append(event)

        strategy_for_execution = _ApprovedEventStrategy(approved_events, quantity)
        result = self._execution.run(ordered, strategy_for_execution, starting_cash=starting_cash)
        return IntegratedBacktestResult(result.fills, tuple(decisions))


class _ApprovedEventStrategy:
    def __init__(self, approved: list[BacktestEvent], quantity: int) -> None:
        self._approved = {(e.timestamp, e.instrument): e for e in approved}
        self._quantity = quantity

    def on_event(self, event: BacktestEvent) -> int:
        return self._quantity if (event.timestamp, event.instrument) in self._approved else 0
