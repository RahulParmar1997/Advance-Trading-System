from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Protocol

from advance_system.storage.contracts import StorageConfig


class AsyncConnection(Protocol):
    async def execute(self, statement: str, *parameters: Any) -> Any: ...

    async def close(self) -> None: ...


class AsyncTransactionConnection(AsyncConnection, Protocol):
    async def transaction(self) -> Any: ...


class AsyncConnectionFactory(Protocol):
    async def __call__(self) -> AsyncConnection: ...


class _PooledAsyncConnection:
    """Adapter that returns an acquired asyncpg connection to its pool on close."""

    def __init__(self, pool: Any, connection: Any) -> None:
        self._pool = pool
        self._connection = connection
        self._released = False

    async def execute(self, statement: str, *parameters: Any) -> Any:
        return await self._connection.execute(statement, *parameters)

    def transaction(self) -> Any:
        return self._connection.transaction()

    async def close(self) -> None:
        if self._released:
            return
        await self._pool.release(self._connection)
        self._released = True


class PostgresOperationalStore:
    """Driver-neutral PostgreSQL adapter with explicit connection lifecycle."""

    def __init__(self, config: StorageConfig, connection_factory: AsyncConnectionFactory) -> None:
        config.validate()
        self._config = config
        self._connection_factory = connection_factory

    @property
    def config(self) -> StorageConfig:
        return self._config

    async def execute(self, statement: str, parameters: tuple[object, ...] = ()) -> None:
        if not statement.strip():
            raise ValueError("statement is required")
        connection = await self._connection_factory()
        try:
            await connection.execute(statement, *parameters)
        finally:
            await connection.close()

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncTransactionConnection]:
        connection = await self._connection_factory()
        transaction_factory = getattr(connection, "transaction", None)
        if not callable(transaction_factory):
            await connection.close()
            raise TypeError("PostgreSQL connection does not support transactions")
        transaction = transaction_factory()
        try:
            async with transaction:
                yield connection  # type: ignore[misc]
        finally:
            await connection.close()

    async def healthcheck(self) -> bool:
        try:
            await self.execute("SELECT 1")
        except Exception:
            return False
        return True


class AsyncpgConnectionFactory:
    """Production connection factory; asyncpg is imported only when this integration is used."""

    def __init__(self, dsn: str, *, min_size: int = 1, max_size: int = 10) -> None:
        if not dsn.strip():
            raise ValueError("PostgreSQL DSN is required")
        if min_size <= 0 or max_size < min_size:
            raise ValueError("invalid PostgreSQL pool size")
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._pool: Any | None = None

    async def __call__(self) -> AsyncConnection:
        if self._pool is None:
            try:
                import asyncpg
            except ImportError as exc:
                raise RuntimeError("asyncpg is required for concrete PostgreSQL integration") from exc
            self._pool = await asyncpg.create_pool(
                dsn=self._dsn,
                min_size=self._min_size,
                max_size=self._max_size,
            )
        connection = await self._pool.acquire()
        return _PooledAsyncConnection(self._pool, connection)

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None


# Explicit alias documents compatibility with the vendor-neutral boundary.
PostgreSQLStoreAdapter = PostgresOperationalStore
