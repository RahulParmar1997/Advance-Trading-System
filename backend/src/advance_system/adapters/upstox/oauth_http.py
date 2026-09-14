from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Protocol
from urllib.parse import urlencode

from advance_system.adapters.upstox.auth import AccessToken, UpstoxAuthClient
from advance_system.config.settings import UpstoxSettings


class HttpClient(Protocol):
    async def post_form(self, url: str, *, data: dict[str, str]) -> tuple[int, str]:
        ...


class UpstoxOAuthHttpClient(UpstoxAuthClient):
    """Thin OAuth adapter. Concrete HTTP library is injected and secrets stay runtime-only."""

    def __init__(self, settings: UpstoxSettings, http: HttpClient) -> None:
        self.settings = settings
        self.http = http

    async def exchange_authorization_code(self, *, code: str, redirect_uri: str) -> AccessToken:
        if not code.strip():
            raise ValueError("authorization code cannot be empty")
        if redirect_uri != self.settings.redirect_uri:
            raise ValueError("redirect URI does not match configured URI")
        return await self._token_request({
            "code": code,
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        })

    async def refresh_access_token(self, *, refresh_token: str) -> AccessToken:
        if not refresh_token.strip():
            raise ValueError("refresh token cannot be empty")
        return await self._token_request({
            "refresh_token": refresh_token,
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
            "grant_type": "refresh_token",
        })

    async def _token_request(self, data: dict[str, str]) -> AccessToken:
        status, body = await self.http.post_form(self.settings.token_url, data=data)
        if status < 200 or status >= 300:
            raise RuntimeError(f"Upstox token request failed with HTTP {status}")
        try:
            payload = json.loads(body)
            value = payload["access_token"]
        except (ValueError, KeyError, TypeError) as exc:
            raise RuntimeError("invalid Upstox token response") from exc
        expires_at = None
        expires_in = payload.get("expires_in")
        if isinstance(expires_in, (int, float)):
            expires_at = datetime.now(timezone.utc).replace(microsecond=0)
            from datetime import timedelta
            expires_at += timedelta(seconds=int(expires_in))
        return AccessToken(value=value, expires_at=expires_at)


def build_authorization_url(settings: UpstoxSettings, *, state: str | None = None) -> str:
    params = {
        "response_type": "code",
        "client_id": settings.client_id,
        "redirect_uri": settings.redirect_uri,
    }
    if state:
        params["state"] = state
    return "https://api.upstox.com/v2/login/authorization/dialog?" + urlencode(params)
