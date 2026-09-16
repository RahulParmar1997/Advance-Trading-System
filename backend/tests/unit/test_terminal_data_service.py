from __future__ import annotations

from dataclasses import dataclass

import pytest

from advance_system.observability.providers import TerminalDataService, TerminalSnapshot


@dataclass
class Provider:
    snapshots: dict[str, TerminalSnapshot]

    def snapshot(self, view: str) -> TerminalSnapshot | None:
        return self.snapshots.get(view)


def test_service_fails_closed_without_provider() -> None:
    response = TerminalDataService().get("market-state")

    assert response.available is False
    assert response.data is None
    assert response.reason == "data_feed_not_connected"


def test_service_exposes_provider_snapshot_without_synthesis() -> None:
    payload = {"instrument": "NSE_EQ|TEST", "last_price": "123.45"}
    provider = Provider({"market-state": TerminalSnapshot("market-state", payload)})

    response = TerminalDataService(provider).get("market-state")

    assert response.available is True
    assert response.reason == "provider_snapshot"
    assert response.data is payload
    assert response.mode == "PAPER"
    assert response.schema_version == "v1"


def test_service_rejects_mismatched_provider_view_fail_closed() -> None:
    provider = Provider({"market-state": TerminalSnapshot("scanner", {"rows": []})})

    response = TerminalDataService(provider).get("market-state")

    assert response.available is False
    assert response.data is None
    assert response.reason == "data_feed_not_connected"


@pytest.mark.parametrize("view", ["market-state", "scanner", "risk", "portfolio"])
def test_provider_snapshot_is_selected_by_view(view: str) -> None:
    payload = {"view": view}
    provider = Provider({view: TerminalSnapshot(view, payload)})

    response = TerminalDataService(provider).get(view)  # type: ignore[arg-type]

    assert response.available is True
    assert response.data == payload
