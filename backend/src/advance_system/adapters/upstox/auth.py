from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol


@dataclass(frozen=True, slots=True)
class AccessToken:
    value: str
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("access token cannot be empty")

    def is_expired(self, *, now: datetime, skew: timedelta = timedelta(seconds=30)) -> bool:
        if self.expires_at is None:
            return False
        return now + skew >= self.expires_at


class TokenProvider(Protocol):
    """Application-facing token contract; implementations own secret storage."""

    async def get_access_token(self) -> AccessToken:
        ...


@dataclass(frozen=True, slots=True)
class StaticTokenProvider:
    """Paper/test provider. Never reads or persists credentials."""

    token: AccessToken

    async def get_access_token(self) -> AccessToken:
        return self.token


class UpstoxAuthClient(Protocol):
    """Boundary for the OAuth/token exchange; HTTP is intentionally outside domain code."""

    async def exchange_authorization_code(self, *, code: str, redirect_uri: str) -> AccessToken:
        ...

    async def refresh_access_token(self, *, refresh_token: str) -> AccessToken:
        ...
