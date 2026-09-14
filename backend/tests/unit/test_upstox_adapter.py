from collections.abc import AsyncIterator, Sequence
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.adapters.upstox.auth import AccessToken, StaticTokenProvider
from advance_system.adapters.upstox.market_data import UpstoxAdapter, UpstoxQuote
from advance_system.ingestion.adapters import Instrument


class FakeUpstoxClient:
    def __init__(self) -> None:
        self.token_seen = None
        self.closed = False

    async def stream_quotes(self, instruments: Sequence[Instrument], access_token: str) -> AsyncIterator[UpstoxQuote]:
        self.token_seen = access_token
        yield UpstoxQuote(
            instrument=instruments[0].instrument,
            timestamp=datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc),
            last_price=Decimal("250.50"),
            bid=Decimal("250.40"),
            ask=Decimal("250.60"),
            volume=1234,
        )

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_upstox_adapter_maps_quotes_and_keeps_token_out_of_raw_quote():
    client = FakeUpstoxClient()
    provider = StaticTokenProvider(AccessToken("test-token"))
    adapter = UpstoxAdapter(client, provider)
    instrument = Instrument("NSE_EQ|TEST", "NSE", "TEST", "EQUITY")

    quotes = [quote async for quote in adapter.stream_quotes([instrument])]
    await adapter.close()

    assert client.token_seen == "test-token"
    assert len(quotes) == 1
    assert quotes[0].instrument == "NSE_EQ|TEST"
    assert quotes[0].ltp == Decimal("250.50")
    assert quotes[0].bid == Decimal("250.40")
    assert quotes[0].ask == Decimal("250.60")
    assert quotes[0].volume == 1234
    assert client.closed


def test_access_token_expiry_with_skew():
    from datetime import timedelta

    now = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)
    token = AccessToken("x", expires_at=now + timedelta(seconds=20))
    assert token.is_expired(now=now, skew=timedelta(seconds=30))
    assert not token.is_expired(now=now, skew=timedelta(seconds=5))
