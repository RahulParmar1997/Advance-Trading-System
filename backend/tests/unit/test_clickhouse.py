from __future__ import annotations

import pytest

from advance_system.storage.clickhouse import ClickHouseAnalyticsStore
from advance_system.storage.contracts import StorageConfig


class FakeConnection:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []
        self.closed = False

    async def execute(self, statement: str, *parameters: object) -> None:
        self.calls.append((statement, parameters))

    async def close(self) -> None:
        self.closed = True


def config() -> StorageConfig:
    return StorageConfig(
        postgres_dsn="postgresql://db.example/ats",
        clickhouse_dsn="https://analytics.example",
        redis_url="redis://cache.example/0",
        parquet_root="s3://ats-research",
    )


@pytest.mark.asyncio
async def test_clickhouse_adapter_executes_and_closes() -> None:
    connection = FakeConnection()

    async def factory() -> FakeConnection:
        return connection

    store = ClickHouseAnalyticsStore(config(), factory)
    await store.execute("SELECT * FROM market_events WHERE instrument = {instrument}", ("NSE_EQ|TEST",))

    assert connection.calls == [
        ("SELECT * FROM market_events WHERE instrument = {instrument}", ("NSE_EQ|TEST",))
    ]
    assert connection.closed is True


@pytest.mark.asyncio
async def test_clickhouse_healthcheck_fails_closed() -> None:
    class BrokenConnection:
        async def execute(self, statement: str, *parameters: object) -> None:
            raise RuntimeError("analytics unavailable")

        async def close(self) -> None:
            pass

    async def factory() -> BrokenConnection:
        return BrokenConnection()

    assert await ClickHouseAnalyticsStore(config(), factory).healthcheck() is False


@pytest.mark.asyncio
async def test_clickhouse_rejects_empty_statement() -> None:
    async def factory() -> FakeConnection:
        return FakeConnection()

    with pytest.raises(ValueError, match="statement"):
        await ClickHouseAnalyticsStore(config(), factory).execute(" ")
