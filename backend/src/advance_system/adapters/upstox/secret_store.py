from __future__ import annotations

from datetime import datetime
from typing import Protocol

from advance_system.adapters.upstox.auth import AccessToken


class SecretStoreError(RuntimeError):
    """Raised when a production secret backend cannot safely serve a token."""


class SecretValueStore(Protocol):
    """Minimal secret-manager boundary; implementations must not persist to local disk."""

    async def get(self, key: str) -> str | None:
        ...

    async def set(self, key: str, value: str) -> None:
        ...

    async def delete(self, key: str) -> None:
        ...


class SecretBackedTokenStore:
    """TokenStore backed by an injected secret manager.

    The serialized value is intentionally small and versioned. No filesystem,
    environment-variable, or logging fallback is used for token persistence.
    """

    _VERSION = "1"

    def __init__(self, secret_store: SecretValueStore, *, key: str) -> None:
        if not key.strip():
            raise ValueError("secret key cannot be empty")
        self._secret_store = secret_store
        self._key = key

    async def load(self) -> AccessToken | None:
        raw = await self._secret_store.get(self._key)
        if raw is None:
            return None
        return self._decode(raw)

    async def save(self, token: AccessToken) -> None:
        await self._secret_store.set(self._key, self._encode(token))

    async def clear(self) -> None:
        await self._secret_store.delete(self._key)

    @classmethod
    def _encode(cls, token: AccessToken) -> str:
        expires = token.expires_at.isoformat() if token.expires_at is not None else ""
        return f"v={cls._VERSION}\nexpires_at={expires}\nvalue={token.value}"

    @classmethod
    def _decode(cls, raw: str) -> AccessToken:
        fields: dict[str, str] = {}
        for line in raw.splitlines():
            if "=" not in line:
                raise SecretStoreError("malformed stored access token")
            key, value = line.split("=", 1)
            fields[key] = value
        if fields.get("v") != cls._VERSION or not fields.get("value", "").strip():
            raise SecretStoreError("unsupported or invalid stored access token")

        expires_raw = fields.get("expires_at", "")
        expires_at = datetime.fromisoformat(expires_raw) if expires_raw else None
        return AccessToken(value=fields["value"], expires_at=expires_at)


class MappingSecretValueStore:
    """In-memory secret-manager double for tests; never use as production storage."""

    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def set(self, key: str, value: str) -> None:
        self.values[key] = value

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)
