from __future__ import annotations

from typing import Any, Protocol

from advance_system.storage.contracts import StorageConfig


class ClickHouseConnection(Protocol):
    async def execute(self, statement: str, *parameters: Any) -> Any: ...

    async def close(self) -> None: ...


class ClickHouseConnectionFactory(Protocol):
    async def __call__(self) -> ClickHouseConnection: ...


class ClickHouseAnalyticsStore:
    """Driver-neutral ClickHouse boundary for analytical reads/writes only."""

    def __init__(self, config: StorageConfig, connection_factory: ClickHouseConnectionFactory) -> None:
        config.validate()
        self._config = config
        self._connection_factory = connection_factory

    async def execute(self, statement: str, parameters: tuple[object, ...] = ()) -> None:
        if not statement.strip():
            raise ValueError("statement is required")
        connection = await self._connection_factory()
        try:
            await connection.execute(statement, *parameters)
        finally:
            await connection.close()

    async def healthcheck(self) -> bool:
        try:
            await self.execute("SELECT 1")
        except Exception:
            return False
        return True


ClickHouseStoreAdapter = ClickHouseAnalyticsStore
