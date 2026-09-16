from __future__ import annotations

import os
from http.server import ThreadingHTTPServer

from advance_system.observability.api import VIEW_PATHS, unavailable_view
from advance_system.observability.metrics import MetricSample, MetricsHandler, MetricsRegistry


class TerminalObservabilityHandler(MetricsHandler):
    """Metrics plus read-only terminal API; no broker or execution authority."""

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        view = VIEW_PATHS.get(self.path)
        if view is None:
            super().do_GET()
            return
        payload = unavailable_view(view).to_json()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    registry = MetricsRegistry()
    registry.set(
        MetricSample(
            "ats_process_up",
            1,
            help_text="Observability process is running.",
        )
    )
    host = os.getenv("ATS_METRICS_HOST", "0.0.0.0")
    port = int(os.getenv("ATS_METRICS_PORT", "8000"))
    handler = type("BoundTerminalObservabilityHandler", (TerminalObservabilityHandler,), {"registry": registry})
    server = ThreadingHTTPServer((host, port), handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
