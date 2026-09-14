import json
from datetime import datetime, timezone

import pytest

from advance_system.adapters.upstox.auth import AccessToken
from advance_system.adapters.upstox.oauth_http import UpstoxOAuthHttpClient, build_authorization_url
from advance_system.adapters.upstox.token_store import MemoryTokenStore
from advance_system.config.settings import UpstoxSettings
from advance_system.ingestion.sequence import SequenceGuard


class FakeHttp:
    def __init__(self, status=200, body=None):
        self.status = status
        self.body = body or json.dumps({"access_token": "runtime-token", "expires_in": 3600})
        self.url = None
        self.data = None

    async def post_form(self, url, *, data):
        self.url = url
        self.data = data
        return self.status, self.body


def settings():
    return UpstoxSettings("client", "secret", "https://localhost/callback")


@pytest.mark.asyncio
async def test_oauth_client_exchanges_code_without_logging_secret():
    http = FakeHttp()
    client = UpstoxOAuthHttpClient(settings(), http)
    token = await client.exchange_authorization_code(code="one-time-code", redirect_uri="https://localhost/callback")
    assert token.value == "runtime-token"
    assert http.data["client_secret"] == "secret"
    assert http.data["grant_type"] == "authorization_code"


def test_authorization_url_contains_required_oauth_parameters():
    url = build_authorization_url(settings(), state="abc")
    assert "response_type=code" in url
    assert "client_id=client" in url
    assert "state=abc" in url
    assert "secret" not in url


@pytest.mark.asyncio
async def test_memory_token_store():
    store = MemoryTokenStore()
    assert await store.load() is None
    token = AccessToken("x", datetime(2026, 1, 2, tzinfo=timezone.utc))
    await store.save(token)
    assert await store.load() == token
    await store.clear()
    assert await store.load() is None


def test_sequence_guard_detects_gap_and_reordering():
    guard = SequenceGuard()
    assert guard.observe("feed", 10).code == "INITIAL"
    assert guard.observe("feed", 11).code == "VALID"
    assert guard.observe("feed", 14).code == "GAP"
    result = guard.observe("feed", 13)
    assert result.code == "OUT_OF_ORDER"
    assert result.accepted is False
