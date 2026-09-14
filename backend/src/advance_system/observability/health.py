from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Mapping


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True, slots=True)
class DependencyStatus:
    name: str
    status: HealthStatus
    detail: str = ""


@dataclass(frozen=True, slots=True)
class HealthReport:
    status: HealthStatus
    checks: tuple[DependencyStatus, ...]

    @property
    def ready(self) -> bool:
        return self.status is HealthStatus.HEALTHY


class HealthChecker:
    """Deterministic health/readiness boundary; checks are side-effect free callables."""

    def __init__(self, checks: Mapping[str, Callable[[], bool]] | None = None) -> None:
        self._checks = dict(checks or {})

    def check(self) -> HealthReport:
        results: list[DependencyStatus] = []
        for name in sorted(self._checks):
            try:
                healthy = bool(self._checks[name]())
                results.append(
                    DependencyStatus(name, HealthStatus.HEALTHY if healthy else HealthStatus.UNHEALTHY)
                )
            except Exception as exc:  # noqa: BLE001 - health must fail closed
                results.append(DependencyStatus(name, HealthStatus.UNHEALTHY, type(exc).__name__))
        overall = HealthStatus.HEALTHY if all(item.status is HealthStatus.HEALTHY for item in results) else HealthStatus.UNHEALTHY
        return HealthReport(overall, tuple(results))

    def readiness(self) -> HealthReport:
        """Return readiness; missing checks fail closed rather than implying production readiness."""
        if not self._checks:
            return HealthReport(HealthStatus.UNHEALTHY, ())
        return self.check()
