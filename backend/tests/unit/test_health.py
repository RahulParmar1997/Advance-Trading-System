from advance_system.observability.health import HealthChecker, HealthStatus


def test_health_is_healthy_when_all_checks_pass() -> None:
    report = HealthChecker({"broker": lambda: True, "market_data": lambda: True}).check()
    assert report.status is HealthStatus.HEALTHY
    assert report.ready
    assert [item.name for item in report.checks] == ["broker", "market_data"]


def test_empty_health_checks_fail_closed() -> None:
    report = HealthChecker().check()
    assert report.status is HealthStatus.UNHEALTHY
    assert not report.ready
    assert report.checks == ()


def test_readiness_fails_closed_without_checks() -> None:
    report = HealthChecker().readiness()
    assert report.status is HealthStatus.UNHEALTHY
    assert not report.ready


def test_unhealthy_dependency_makes_readiness_fail() -> None:
    report = HealthChecker({"market_data": lambda: False}).readiness()
    assert report.status is HealthStatus.UNHEALTHY
    assert report.checks[0].status is HealthStatus.UNHEALTHY


def test_check_exception_fails_closed_and_exposes_exception_type_only() -> None:
    def broken() -> bool:
        raise RuntimeError("connection details must not leak")

    report = HealthChecker({"database": broken}).check()
    assert report.status is HealthStatus.UNHEALTHY
    assert report.checks[0].detail == "RuntimeError"
    assert "connection details" not in report.checks[0].detail


def test_check_order_is_deterministic() -> None:
    report = HealthChecker({"z": lambda: True, "a": lambda: True}).check()
    assert [item.name for item in report.checks] == ["a", "z"]
