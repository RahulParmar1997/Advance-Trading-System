from __future__ import annotations

from typing import Any, Protocol

from advance_system.storage.contracts import RedisStore, StorageConfig


class RedisConnection(Protocol):
    async def get(self, key: str) -> bytes | None: ...
    async def set(self, key: str, value: bytes, *, ex: int | None = None) -> Any: ...
    async def delete(self, key: str) -> Any: ...
    async def close(self) -> Any: ...


class RedisConnectionFactory(Protocol):
    async def __call__(self) -> RedisConnection: ...


class RedisHotStateStore:
    """Ephemeral Redis state; orders and positions must remain in PostgreSQL."""

    def __init__(self, config: StorageConfig, connection_factory: RedisConnectionFactory) -> None:
        config.validate()
        self._config = config
        self._connection_factory = connection_factory

    async def get(self, key: str) -> bytes | None:
        self._validate_key(key)
        connection = await self._connection_factory()
        try:
            return await connection.get(key)
        finally:
            await connection.close()

    async def set(self, key: str, value: bytes, *, ttl_seconds: int | None = None) -> None:
        self._validate_key(key)
        if not isinstance(value, bytes):
            raise TypeError("Redis values must be bytes")
        if ttl_seconds is not None and ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        connection = await self._connection_factory()
        try:
            await connection.set(key, value, ex=ttl_seconds)
        finally:
            await connection.close()

    async def delete(self, key: str) -> None:
        self._validate_key(key)
        connection = await self._connection_factory()
        try:
            await connection.delete(key)
        finally:
            await connection.close()

    async def healthcheck(self) -> bool:
        try:
            await self.set("__ats_healthcheck__", b"1", ttl_seconds=1)
        except Exception:
            return False
        return True

    @staticmethod
    def _validate_key(key: str) -> None:
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Redis key is required")
        if key.startswith(("order:", "position:")):
            raise ValueError("Redis cannot be used as order or position source of truth")


RedisStoreAdapter = RedisHotStateStore
