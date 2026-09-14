from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Sequence

from advance_system.backtest.engine import BacktestEvent, BacktestResult, EventDrivenBacktester


@dataclass(frozen=True, slots=True)
class WalkForwardWindow:
    train: tuple[BacktestEvent, ...]
    test: tuple[BacktestEvent, ...]

    def validate(self) -> None:
        if not self.train or not self.test:
            raise ValueError("walk-forward train and test windows must be non-empty")
        if self.train[-1].timestamp >= self.test[0].timestamp:
            raise ValueError("walk-forward test data must start after training data")


@dataclass(frozen=True, slots=True)
class WalkForwardResult:
    window_index: int
    train_events: int
    test_events: int
    test_result: BacktestResult


class WalkForwardValidator:
    """Builds chronological train/test windows without allowing test data into training."""

    def windows(
        self,
        events: Sequence[BacktestEvent],
        *,
        train_size: int,
        test_size: int,
        step: int | None = None,
    ) -> tuple[WalkForwardWindow, ...]:
        if train_size <= 0 or test_size <= 0:
            raise ValueError("train_size and test_size must be positive")
        step = test_size if step is None else step
        if step <= 0:
            raise ValueError("step must be positive")
        ordered = tuple(sorted(events, key=lambda event: event.timestamp))
        for event in ordered:
            event.validate()
        result: list[WalkForwardWindow] = []
        start = 0
        while start + train_size + test_size <= len(ordered):
            window = WalkForwardWindow(
                train=ordered[start : start + train_size],
                test=ordered[start + train_size : start + train_size + test_size],
            )
            window.validate()
            result.append(window)
            start += step
        return tuple(result)

    def run(
        self,
        events: Sequence[BacktestEvent],
        strategy_factory: Callable[[tuple[BacktestEvent, ...]], object],
        *,
        train_size: int,
        test_size: int,
        starting_cash: Decimal,
        step: int | None = None,
        backtester: EventDrivenBacktester | None = None,
    ) -> tuple[WalkForwardResult, ...]:
        engine = backtester or EventDrivenBacktester()
        results: list[WalkForwardResult] = []
        for index, window in enumerate(self.windows(events, train_size=train_size, test_size=test_size, step=step)):
            strategy = strategy_factory(window.train)
            test_result = engine.run(window.test, strategy, starting_cash=starting_cash)
            results.append(WalkForwardResult(index, len(window.train), len(window.test), test_result))
        return tuple(results)
