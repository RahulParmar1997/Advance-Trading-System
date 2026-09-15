from __future__ import annotations

import pytest

from advance_system.storage.contracts import StorageConfig
from advance_system.storage.postgres import PostgresOperationalStore


class FakeConnection:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    async def execute(self, statement: str, *parameters: object) -> None:
        self.calls.append((statement, parameters))


@pytest.fixture
def config() -> StorageConfig:
    return StorageConfig(
        postgres_dsn="postgresql://db.example/ats",
        clickhouse_dsn="https://analytics.example",
        redis_url="redis://cache.example/0",
        parquet_root="s3://ats-research",
    )


@pytest.mark.asyncio
async def test_postgres_adapter_delegates_parameterized_statement(config: StorageConfig) -> None:
    connection = FakeConnection()

    async def factory() -> FakeConnection:
        return connection

    store = PostgresOperationalStore(config, factory)
    await store.execute("SELECT * FROM orders WHERE order_id = $1", ("order-1",))

    assert connection.calls == [("SELECT * FROM orders WHERE order_id = $1", (("order-1",),))]


@pytest.mark.asyncio
async def test_postgres_healthcheck_fails_closed(config: StorageConfig) -> None:
    class BrokenConnection:
        async def execute(self, statement: str, *parameters: object) -> None:
            raise RuntimeError("database unavailable")

    async def factory() -> BrokenConnection:
        return BrokenConnection()

    store = PostgresOperationalStore(config, factory)
    assert await store.healthcheck() is False


@pytest.mark.asyncio
async def test_postgres_rejects_empty_statement(config: StorageConfig) -> None:
    async def factory() -> FakeConnection:
        return FakeConnection()

    store = PostgresOperationalStore(config, factory)
    with pytest.raises(ValueError, match="statement"):
        await store.execute("   ")
