from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from random import Random
from typing import Sequence


@dataclass(frozen=True, slots=True)
class MonteCarloResult:
    simulations: int
    mean_total_pnl: Decimal
    median_total_pnl: Decimal
    worst_total_pnl: Decimal
    best_total_pnl: Decimal
    loss_probability: Decimal


@dataclass(frozen=True, slots=True)
class SensitivityPoint:
    parameter: str
    value: Decimal
    total_pnl: Decimal


class BacktestSensitivity:
    """Deterministic research helpers; never connected to live execution."""

    def monte_carlo_resample(
        self,
        trade_pnls: Sequence[Decimal],
        *,
        simulations: int = 1000,
        seed: int = 0,
    ) -> MonteCarloResult:
        if not trade_pnls:
            raise ValueError("trade_pnls must not be empty")
        if simulations <= 0:
            raise ValueError("simulations must be positive")
        values = tuple(trade_pnls)
        rng = Random(seed)
        totals = [sum((rng.choice(values) for _ in values), Decimal("0")) for _ in range(simulations)]
        ordered = sorted(totals)
        losses = sum(1 for total in totals if total < 0)
        return MonteCarloResult(
            simulations,
            sum(totals, Decimal("0")) / Decimal(simulations),
            ordered[len(ordered) // 2],
            ordered[0],
            ordered[-1],
            Decimal(losses) / Decimal(simulations),
        )

    def cost_sensitivity(
        self,
        gross_trade_pnls: Sequence[Decimal],
        notionals: Sequence[Decimal],
        fee_bps: Sequence[Decimal],
    ) -> tuple[SensitivityPoint, ...]:
        if len(gross_trade_pnls) != len(notionals) or not gross_trade_pnls:
            raise ValueError("gross_trade_pnls and notionals must have equal non-zero length")
        if any(n <= 0 for n in notionals) or any(b < 0 for b in fee_bps):
            raise ValueError("notionals must be positive and fee_bps cannot be negative")
        return tuple(
            SensitivityPoint(
                "fee_bps",
                bps,
                sum((p - n * bps / Decimal("10000") for p, n in zip(gross_trade_pnls, notionals)), Decimal("0")),
            )
            for bps in fee_bps
        )

    def capacity_sensitivity(
        self,
        trade_pnls: Sequence[Decimal],
        trade_notionals: Sequence[Decimal],
        participation_rates: Sequence[Decimal],
        market_volumes: Sequence[Decimal],
    ) -> tuple[SensitivityPoint, ...]:
        self._validate_parallel(trade_pnls, trade_notionals, market_volumes)
        if any(n < 0 for n in trade_notionals) or any(v <= 0 for v in market_volumes):
            raise ValueError("trade notionals cannot be negative and market volumes must be positive")
        result: list[SensitivityPoint] = []
        for rate in participation_rates:
            if not Decimal("0") < rate <= Decimal("1"):
                raise ValueError("participation rate must be in (0, 1]")
            total = sum(
                (p if n <= volume * rate else Decimal("0") for p, n, volume in zip(trade_pnls, trade_notionals, market_volumes)),
                Decimal("0"),
            )
            result.append(SensitivityPoint("participation_rate", rate, total))
        return tuple(result)

    def regime_sensitivity(
        self,
        trade_pnls: Sequence[Decimal],
        regimes: Sequence[str],
    ) -> dict[str, Decimal]:
        """Aggregate observed trade P&L by caller-supplied historical regime label."""
        if len(trade_pnls) != len(regimes) or not trade_pnls:
            raise ValueError("trade_pnls and regimes must have equal non-zero length")
        if any(not regime.strip() for regime in regimes):
            raise ValueError("regime labels must be non-empty")
        result: dict[str, Decimal] = {}
        for pnl, regime in zip(trade_pnls, regimes):
            result[regime] = result.get(regime, Decimal("0")) + pnl
        return dict(sorted(result.items()))

    @staticmethod
    def _validate_parallel(*series: Sequence[object]) -> None:
        if not series or not series[0] or any(len(values) != len(series[0]) for values in series):
            raise ValueError("sensitivity inputs must have equal non-zero length")
