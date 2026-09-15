from __future__ import annotations

import pytest

from advance_system.storage.contracts import StorageConfig, StorageMode


def valid_config() -> StorageConfig:
    return StorageConfig(
        postgres_dsn="postgresql://db.example/ats",
        clickhouse_dsn="https://analytics.example",
        redis_url="rediss://cache.example:6379/0",
        parquet_root="s3://ats-research",
    )


def test_storage_config_validates_all_backend_endpoints() -> None:
    config = valid_config()
    config.validate()
    assert config.mode is StorageMode.PAPER


def test_storage_config_loads_endpoints_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ATS_POSTGRES_DSN", "postgresql://db.example/ats")
    monkeypatch.setenv("ATS_CLICKHOUSE_DSN", "https://analytics.example")
    monkeypatch.setenv("ATS_REDIS_URL", "redis://cache.example/0")
    monkeypatch.setenv("ATS_PARQUET_ROOT", "file:///data/research")
    monkeypatch.setenv("ATS_STORAGE_MODE", "PAPER")

    config = StorageConfig.from_environment()

    assert config.parquet_root == "file:///data/research"
    assert config.mode is StorageMode.PAPER


def test_storage_config_fails_closed_when_endpoint_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ATS_POSTGRES_DSN", raising=False)
    monkeypatch.setenv("ATS_CLICKHOUSE_DSN", "https://analytics.example")
    monkeypatch.setenv("ATS_REDIS_URL", "redis://cache.example/0")
    monkeypatch.setenv("ATS_PARQUET_ROOT", "s3://ats-research")

    with pytest.raises(RuntimeError, match="postgres_dsn"):
        StorageConfig.from_environment()


def test_storage_config_rejects_unsupported_endpoint_scheme() -> None:
    config = valid_config()
    invalid = StorageConfig(
        postgres_dsn="ftp://db.example/ats",
        clickhouse_dsn=config.clickhouse_dsn,
        redis_url=config.redis_url,
        parquet_root=config.parquet_root,
    )

    with pytest.raises(ValueError, match="postgres_dsn"):
        invalid.validate()


def test_storage_config_does_not_use_http_for_parquet_root() -> None:
    config = StorageConfig(
        postgres_dsn="postgresql://db.example/ats",
        clickhouse_dsn="https://analytics.example",
        redis_url="redis://cache.example/0",
        parquet_root="https://objects.example/data",
    )

    with pytest.raises(ValueError, match="parquet_root"):
        config.validate()
