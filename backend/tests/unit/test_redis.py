from __future__ import annotations

import pytest

from advance_system.storage.contracts import StorageConfig
from advance_system.storage.redis import RedisHotStateStore


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, bytes] = {}
        self.calls: list[tuple[str, object]] = []
        self.closed = False

    async def get(self, key: str) -> bytes | None:
        self.calls.append(("get", key))
        return self.values.get(key)

    async def set(self, key: str, value: bytes, *, ex: int | None = None) -> bool:
        self.calls.append(("set", (key, value, ex)))
        self.values[key] = value
        return True

    async def delete(self, key: str) -> int:
        self.calls.append(("delete", key))
        return int(self.values.pop(key, None) is not None)

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
async def test_redis_set_get_delete_and_ttl() -> None:
    connection = FakeRedis()

    async def factory() -> FakeRedis:
        return connection

    store = RedisHotStateStore(config(), factory)
    await store.set("freshness:NSE", b"ok", ttl_seconds=30)
    assert await store.get("freshness:NSE") == b"ok"
    await store.delete("freshness:NSE")

    assert ("set", ("freshness:NSE", b"ok", 30)) in connection.calls
    assert connection.closed is True


@pytest.mark.asyncio
async def test_redis_rejects_order_and_position_keys() -> None:
    async def factory() -> FakeRedis:
        return FakeRedis()

    store = RedisHotStateStore(config(), factory)
    with pytest.raises(ValueError, match="source of truth"):
        await store.set("order:123", b"state")
    with pytest.raises(ValueError, match="source of truth"):
        await store.get("position:NSE_EQ|TEST")


@pytest.mark.asyncio
async def test_redis_rejects_invalid_ttl_and_value() -> None:
    async def factory() -> FakeRedis:
        return FakeRedis()

    store = RedisHotStateStore(config(), factory)
    with pytest.raises(ValueError, match="ttl_seconds"):
        await store.set("cache:key", b"x", ttl_seconds=0)
    with pytest.raises(TypeError, match="bytes"):
        await store.set("cache:key", "x")  # type: ignore[arg-type]
