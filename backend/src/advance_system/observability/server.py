from __future__ import annotations

import os

from advance_system.observability.metrics import MetricsRegistry, MetricSample, create_metrics_server


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
    server = create_metrics_server(registry, host=host, port=port)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
