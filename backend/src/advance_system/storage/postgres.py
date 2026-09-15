from __future__ import annotations

from typing import Any, Protocol

from advance_system.storage.contracts import PostgreSQLStore, StorageConfig


class AsyncConnection(Protocol):
    async def execute(self, statement: str, *parameters: Any) -> Any: ...


class AsyncConnectionFactory(Protocol):
    async def __call__(self) -> AsyncConnection: ...


class PostgresOperationalStore:
    """Small repository boundary; driver lifecycle is injected and never reaches domain code."""

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
        await connection.execute(statement, *parameters)

    async def healthcheck(self) -> bool:
        try:
            await self.execute("SELECT 1")
        except Exception:
            return False
        return True


# Explicit alias documents compatibility with the vendor-neutral boundary.
PostgreSQLStoreAdapter = PostgresOperationalStore
