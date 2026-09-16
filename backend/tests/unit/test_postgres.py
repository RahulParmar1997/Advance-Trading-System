from __future__ import annotations

import asyncio

import pytest

from advance_system.storage.contracts import StorageConfig
from advance_system.storage.postgres import AsyncpgConnectionFactory, PostgresOperationalStore


class FakeTransaction:
    def __init__(self) -> None:
        self.entered = False
        self.exited = False

    async def __aenter__(self) -> "FakeTransaction":
        self.entered = True
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        self.exited = True
        return False


class FakeConnection:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []
        self.closed = False
        self.tx = FakeTransaction()

    async def execute(self, statement: str, *parameters: object) -> None:
        self.calls.append((statement, parameters))

    def transaction(self) -> FakeTransaction:
        return self.tx

    async def close(self) -> None:
        self.closed = True


@pytest.fixture
def config() -> StorageConfig:
    return StorageConfig(
        postgres_dsn="postgresql://db.example/ats",
        clickhouse_dsn="https://analytics.example",
        redis_url="redis://cache.example/0",
        parquet_root="s3://ats-research",
    )


@pytest.mark.asyncio
async def test_postgres_adapter_delegates_parameterized_statement_and_closes(config: StorageConfig) -> None:
    connection = FakeConnection()

    async def factory() -> FakeConnection:
        return connection

    store = PostgresOperationalStore(config, factory)
    await store.execute("SELECT * FROM orders WHERE order_id = $1", ("order-1",))

    assert connection.calls == [("SELECT * FROM orders WHERE order_id = $1", ("order-1",))]
    assert connection.closed is True


@pytest.mark.asyncio
async def test_postgres_transaction_commits_and_closes(config: StorageConfig) -> None:
    connection = FakeConnection()

    async def factory() -> FakeConnection:
        return connection

    store = PostgresOperationalStore(config, factory)
    async with store.transaction() as tx:
        await tx.execute("UPDATE positions SET quantity = $1", 10)

    assert connection.tx.entered is True
    assert connection.tx.exited is True
    assert connection.closed is True
    assert connection.calls == [("UPDATE positions SET quantity = $1", (10,))]


@pytest.mark.asyncio
async def test_postgres_transaction_closes_on_failure(config: StorageConfig) -> None:
    connection = FakeConnection()

    async def factory() -> FakeConnection:
        return connection

    store = PostgresOperationalStore(config, factory)
    with pytest.raises(RuntimeError, match="rollback"):
        async with store.transaction() as tx:
            await tx.execute("UPDATE orders SET state = $1", "FAILED")
            raise RuntimeError("rollback")

    assert connection.tx.exited is True
    assert connection.closed is True


@pytest.mark.asyncio
async def test_postgres_transaction_requires_transaction_capability(config: StorageConfig) -> None:
    class NoTransactionConnection:
        async def execute(self, statement: str, *parameters: object) -> None:
            pass

        async def close(self) -> None:
            pass

    async def factory() -> NoTransactionConnection:
        return NoTransactionConnection()

    store = PostgresOperationalStore(config, factory)
    with pytest.raises(TypeError, match="transactions"):
        async with store.transaction():
            pass


@pytest.mark.asyncio
async def test_postgres_healthcheck_fails_closed(config: StorageConfig) -> None:
    class BrokenConnection:
        async def execute(self, statement: str, *parameters: object) -> None:
            raise RuntimeError("database unavailable")

        async def close(self) -> None:
            pass

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


@pytest.mark.asyncio
async def test_asyncpg_factory_returns_connection_to_pool(monkeypatch: pytest.MonkeyPatch) -> None:
    connection = FakeConnection()

    class FakePool:
        def __init__(self) -> None:
            self.released: list[object] = []
            self.closed = False

        async def acquire(self) -> FakeConnection:
            return connection

        async def release(self, acquired: object) -> None:
            self.released.append(acquired)

        async def close(self) -> None:
            self.closed = True

    pool = FakePool()

    class FakeAsyncpg:
        @staticmethod
        async def create_pool(*, dsn: str, min_size: int, max_size: int) -> FakePool:
            assert dsn == "postgresql://db.example/ats"
            assert min_size == 2
            assert max_size == 4
            return pool

    monkeypatch.setitem(__import__("sys").modules, "asyncpg", FakeAsyncpg)
    factory = AsyncpgConnectionFactory("postgresql://db.example/ats", min_size=2, max_size=4)

    acquired = await factory()
    await acquired.execute("SELECT 1")
    await acquired.close()
    await acquired.close()

    assert connection.calls == [("SELECT 1", ())]
    assert pool.released == [connection]
    assert connection.closed is False

    await factory.close()
    assert pool.closed is True


@pytest.mark.asyncio
async def test_asyncpg_factory_initializes_one_pool_for_concurrent_first_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = FakeConnection()
    create_started = asyncio.Event()
    release_create = asyncio.Event()
    create_calls = 0

    class FakePool:
        async def acquire(self) -> FakeConnection:
            return connection

        async def release(self, acquired: object) -> None:
            pass

        async def close(self) -> None:
            pass

    pool = FakePool()

    class FakeAsyncpg:
        @staticmethod
        async def create_pool(*, dsn: str, min_size: int, max_size: int) -> FakePool:
            nonlocal create_calls
            assert dsn == "postgresql://db.example/ats"
            assert min_size == 1
            assert max_size == 2
            create_calls += 1
            create_started.set()
            await release_create.wait()
            return pool

    monkeypatch.setitem(__import__("sys").modules, "asyncpg", FakeAsyncpg)
    factory = AsyncpgConnectionFactory("postgresql://db.example/ats", min_size=1, max_size=2)

    first = asyncio.create_task(factory())
    await create_started.wait()
    second = asyncio.create_task(factory())
    await asyncio.sleep(0)
    release_create.set()

    acquired_first, acquired_second = await asyncio.gather(first, second)

    assert create_calls == 1
    assert acquired_first is not acquired_second
    await acquired_first.close()
    await acquired_second.close()
    await factory.close()
