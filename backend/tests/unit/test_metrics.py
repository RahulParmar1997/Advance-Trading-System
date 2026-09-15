from __future__ import annotations

from http.client import HTTPConnection
from threading import Thread

import pytest

from advance_system.observability.metrics import MetricsRegistry, MetricSample, create_metrics_server


def test_render_is_deterministic_and_prometheus_compatible() -> None:
    registry = MetricsRegistry()
    registry.set(MetricSample("ats_health", 1, help_text="Backend health state."))
    registry.increment("ats_requests_total", labels={"route": "/metrics"})
    registry.increment("ats_requests_total", labels={"route": "/metrics"})

    assert registry.render().decode() == (
        '# HELP ats_health Backend health state.\n'
        '# TYPE ats_health gauge\n'
        'ats_health 1\n'
        '# TYPE ats_requests_total counter\n'
        'ats_requests_total{route="/metrics"} 2\n'
    )


def test_metric_labels_are_escaped_and_duplicate_labels_rejected() -> None:
    registry = MetricsRegistry()
    registry.set(MetricSample("ats_events", 1, labels=(("message", 'a"b\\c\nd'),)))

    assert 'message="a\\"b\\\\c\\nd"' in registry.render().decode()
    with pytest.raises(ValueError, match="duplicate metric label"):
        registry.set(MetricSample("ats_events", 1, labels=(("x", "1"), ("x", "2"))))


def test_metrics_registry_rejects_counter_decrement_and_gauge_increment() -> None:
    registry = MetricsRegistry()
    registry.set(MetricSample("ats_gauge", 1))

    with pytest.raises(ValueError, match="non-negative"):
        registry.increment("ats_counter", -1)
    with pytest.raises(ValueError, match="cannot increment a gauge"):
        registry.increment("ats_gauge")


def test_metrics_http_endpoint_is_read_only() -> None:
    registry = MetricsRegistry()
    registry.set(MetricSample("ats_health", 1))
    server = create_metrics_server(registry, host="127.0.0.1", port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = HTTPConnection(*server.server_address, timeout=2)
        connection.request("GET", "/metrics")
        response = connection.getresponse()
        assert response.status == 200
        assert response.getheader("Content-Type") == "text/plain; version=0.0.4; charset=utf-8"
        assert response.read() == b"# TYPE ats_health gauge\nats_health 1\n"
        connection.close()

        connection = HTTPConnection(*server.server_address, timeout=2)
        connection.request("POST", "/metrics")
        assert connection.getresponse().status == 405
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
