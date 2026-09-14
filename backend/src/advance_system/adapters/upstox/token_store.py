from __future__ import annotations

from typing import Protocol

from advance_system.adapters.upstox.auth import AccessToken


class TokenStore(Protocol):
    async def load(self) -> AccessToken | None:
        ...

    async def save(self, token: AccessToken) -> None:
        ...

    async def clear(self) -> None:
        ...


class MemoryTokenStore:
    """Process-local store suitable for PAPER/testing; never persists secrets to disk."""

    def __init__(self) -> None:
        self._token: AccessToken | None = None

    async def load(self) -> AccessToken | None:
        return self._token

    async def save(self, token: AccessToken) -> None:
        self._token = token

    async def clear(self) -> None:
        self._token = None
