from __future__ import annotations

import subprocess
import uuid

import pytest


def run_compose(*args: str) -> str:
    result = subprocess.run(
        ["docker", "compose", "exec", "-T", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


@pytest.mark.integration
def test_postgres_clickhouse_and_redis_application_operations() -> None:
    marker = f"ats_ci_{uuid.uuid4().hex}"

    postgres = run_compose(
        "postgres",
        "psql",
        "-U",
        "advance_trading",
        "-d",
        "advance_trading",
        "-tAc",
        f"CREATE TEMP TABLE {marker}(value integer); INSERT INTO {marker} VALUES (42); SELECT value FROM {marker};",
    )
    assert postgres == "42"

    clickhouse = run_compose(
        "clickhouse",
        "wget",
        "-qO-",
        "--post-data=SELECT 40 + 2",
        "http://127.0.0.1:8123/",
    )
    assert clickhouse == "42"

    key = f"ats:ci:{marker}"
    run_compose("redis", "redis-cli", "SET", key, "42")
    redis_value = run_compose("redis", "redis-cli", "GET", key)
    assert redis_value == "42"
    run_compose("redis", "redis-cli", "DEL", key)
    assert run_compose("redis", "redis-cli", "GET", key) == ""
