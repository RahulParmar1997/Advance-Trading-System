from __future__ import annotations

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from typing import Mapping

CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"


@dataclass(frozen=True, slots=True)
class MetricSample:
    name: str
    value: float
    labels: tuple[tuple[str, str], ...] = ()
    help_text: str = ""
    metric_type: str = "gauge"

    def validate(self) -> None:
        if not self.name or not self.name.replace("_", "a").isalnum() or self.name[0].isdigit():
            raise ValueError("invalid metric name")
        if self.metric_type not in {"counter", "gauge"}:
            raise ValueError("unsupported metric type")
        if any(not key or not key.replace("_", "a").isalnum() or key[0].isdigit() for key, _ in self.labels):
            raise ValueError("invalid metric label name")
        if len({key for key, _ in self.labels}) != len(self.labels):
            raise ValueError("duplicate metric label")


class MetricsRegistry:
    """Thread-safe observational metrics registry; it has no execution authority."""

    def __init__(self) -> None:
        self._samples: dict[tuple[str, tuple[tuple[str, str], ...]], MetricSample] = {}
        self._lock = Lock()

    def set(self, sample: MetricSample) -> None:
        sample.validate()
        with self._lock:
            self._samples[(sample.name, sample.labels)] = sample

    def increment(self, name: str, amount: float = 1.0, labels: Mapping[str, str] | None = None) -> None:
        if amount < 0:
            raise ValueError("counter increment must be non-negative")
        normalized = tuple(sorted((labels or {}).items()))
        with self._lock:
            current = self._samples.get((name, normalized))
            if current is None:
                current = MetricSample(name, 0.0, normalized, metric_type="counter")
            if current.metric_type != "counter":
                raise ValueError("cannot increment a gauge")
            self._samples[(name, normalized)] = MetricSample(
                name, current.value + amount, normalized, current.help_text, "counter"
            )

    def render(self) -> bytes:
        with self._lock:
            samples = tuple(sorted(self._samples.values(), key=lambda item: (item.name, item.labels)))
        lines: list[str] = []
        seen: set[str] = set()
        for sample in samples:
            if sample.name not in seen:
                if sample.help_text:
                    lines.append(f"# HELP {sample.name} {sample.help_text}")
                lines.append(f"# TYPE {sample.name} {sample.metric_type}")
                seen.add(sample.name)
            labels = ""
            if sample.labels:
                labels = "{" + ",".join(f'{key}="{_escape(value)}"' for key, value in sample.labels) + "}"
            lines.append(f"{sample.name}{labels} {_format_value(sample.value)}")
        return ("\n".join(lines) + ("\n" if lines else "")).encode("utf-8")


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def _format_value(value: float) -> str:
    return str(int(value)) if value.is_integer() else repr(value)


class MetricsHandler(BaseHTTPRequestHandler):
    registry: MetricsRegistry

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path != "/metrics":
            self.send_error(404)
            return
        payload = self.registry.render()
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPE)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self.send_error(405)

    def do_PUT(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self.send_error(405)

    def do_DELETE(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self.send_error(405)

    def log_message(self, format: str, *args: object) -> None:
        return


def create_metrics_server(registry: MetricsRegistry, host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    if not (0 <= port <= 65535):
        raise ValueError("port must be between 0 and 65535")

    handler = type("BoundMetricsHandler", (MetricsHandler,), {"registry": registry})
    return ThreadingHTTPServer((host, port), handler)
