from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def test_compose_exposes_prometheus_with_read_only_config() -> None:
    compose = (REPOSITORY_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "  prometheus:" in compose
    assert "image: prom/prometheus:v2.55.1" in compose
    assert "./deploy/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro" in compose
    assert '"${ATS_PROMETHEUS_PORT:-9090}:9090"' in compose


def test_prometheus_scrapes_backend_metrics_endpoint() -> None:
    config = (
        REPOSITORY_ROOT / "deploy" / "prometheus" / "prometheus.yml"
    ).read_text(encoding="utf-8")

    assert "metrics_path: /metrics" in config
    assert 'targets: ["backend:8000"]' in config
