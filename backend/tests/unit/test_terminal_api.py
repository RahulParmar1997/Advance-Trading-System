from __future__ import annotations

import json
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from advance_system.observability.api import VIEW_PATHS, TerminalViewResponse, unavailable_view
from advance_system.observability.metrics import MetricSample, MetricsRegistry
from advance_system.observability.server import TerminalObservabilityHandler
from http.server import ThreadingHTTPServer


def test_terminal_view_contract_is_versioned_and_does_not_fabricate_data() -> None:
    response = unavailable_view("market-state")

    assert isinstance(response, TerminalViewResponse)
    assert response.schema_version == "v1"
    assert response.view == "market-state"
    assert response.mode == "PAPER"
    assert response.available is False
    assert response.reason == "data_feed_not_connected"
    assert response.data is None


def test_all_terminal_views_have_explicit_read_only_routes() -> None:
    assert VIEW_PATHS == {
        "/api/v1/market-state": "market-state",
        "/api/v1/scanner": "scanner",
        "/api/v1/risk": "risk",
        "/api/v1/portfolio": "portfolio",
    }


def test_terminal_api_serves_json_and_rejects_mutating_methods() -> None:
    registry = MetricsRegistry()
    registry.set(MetricSample("ats_process_up", 1))
    handler = type("BoundHandler", (TerminalObservabilityHandler,), {"registry": registry})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/api/v1/risk"
        with urlopen(url) as response:
            body = json.loads(response.read())
            assert response.status == 200
            assert response.headers["Content-Type"] == "application/json; charset=utf-8"
            assert body["schema_version"] == "v1"
            assert body["view"] == "risk"
            assert body["available"] is False
            assert body["data"] is None

        try:
            urlopen(Request(url, method="POST", data=b"{}"))
        except HTTPError as error:
            assert error.code == 405
        else:
            raise AssertionError("POST must be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
