from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StrategySignal:
    strategy_id: str
    strategy_version: str
    instrument_id: str
    direction: str
    entry: float
    stop: float
    targets: tuple[float, ...]
    metadata: dict[str, Any]


class Strategy(ABC):
    id: str
    version: str

    @abstractmethod
    def required_features(self) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, state: Any) -> StrategySignal | None:
        raise NotImplementedError
