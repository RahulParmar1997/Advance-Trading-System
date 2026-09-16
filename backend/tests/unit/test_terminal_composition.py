from __future__ import annotations

from advance_system.observability.metrics import MetricsRegistry
from advance_system.observability.providers import TerminalSnapshot
from advance_system.observability.server import build_observability_handler


class StaticTerminalProvider:
    def snapshot(self, view: str) -> TerminalSnapshot | None:
        if view != "risk":
            return None
        return TerminalSnapshot(view=view, data={"source": "authoritative-test-provider"})


def test_observability_handler_composition_injects_terminal_provider() -> None:
    handler = build_observability_handler(MetricsRegistry(), StaticTerminalProvider())

    response = handler.terminal_service.get("risk")

    assert response.available is True
    assert response.reason == "provider_snapshot"
    assert response.data == {"source": "authoritative-test-provider"}


def test_observability_handler_composition_without_provider_remains_fail_closed() -> None:
    handler = build_observability_handler(MetricsRegistry())

    response = handler.terminal_service.get("portfolio")

    assert response.available is False
    assert response.reason == "data_feed_not_connected"
    assert response.data is None
