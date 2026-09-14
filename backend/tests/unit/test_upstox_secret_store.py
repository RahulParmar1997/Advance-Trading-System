import asyncio
from datetime import datetime, timezone

import pytest

from advance_system.adapters.upstox.auth import AccessToken
from advance_system.adapters.upstox.secret_store import (
    MappingSecretValueStore,
    SecretBackedTokenStore,
    SecretStoreError,
)


def test_secret_backed_store_round_trips_token_and_expiry() -> None:
    async def scenario() -> None:
        backend = MappingSecretValueStore()
        store = SecretBackedTokenStore(backend, key="upstox/access-token")
        token = AccessToken("test-token", datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc))

        await store.save(token)

        assert await store.load() == token
        assert backend.values["upstox/access-token"].startswith("v=1\nexpires_at=")
        assert "test-token" in backend.values["upstox/access-token"]

    asyncio.run(scenario())


def test_clear_removes_secret() -> None:
    async def scenario() -> None:
        backend = MappingSecretValueStore()
        store = SecretBackedTokenStore(backend, key="upstox/access-token")
        await store.save(AccessToken("test-token"))

        await store.clear()

        assert await store.load() is None
        assert backend.values == {}

    asyncio.run(scenario())


def test_missing_secret_returns_none_without_local_fallback() -> None:
    async def scenario() -> None:
        backend = MappingSecretValueStore()
        store = SecretBackedTokenStore(backend, key="upstox/access-token")

        assert await store.load() is None
        assert backend.values == {}

    asyncio.run(scenario())


def test_invalid_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="secret key cannot be empty"):
        SecretBackedTokenStore(MappingSecretValueStore(), key=" ")


def test_malformed_secret_fails_closed() -> None:
    async def scenario() -> None:
        backend = MappingSecretValueStore()
        backend.values["upstox/access-token"] = "not-a-token"
        store = SecretBackedTokenStore(backend, key="upstox/access-token")

        with pytest.raises(SecretStoreError):
            await store.load()

    asyncio.run(scenario())


def test_unsupported_secret_version_fails_closed() -> None:
    async def scenario() -> None:
        backend = MappingSecretValueStore()
        backend.values["upstox/access-token"] = "v=99\nexpires_at=\nvalue=test-token"
        store = SecretBackedTokenStore(backend, key="upstox/access-token")

        with pytest.raises(SecretStoreError):
            await store.load()

    asyncio.run(scenario())
