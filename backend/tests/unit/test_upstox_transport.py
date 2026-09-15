import asyncio
from collections.abc import AsyncIterator, Sequence
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from advance_system.adapters.upstox.market_data import UpstoxQuote
from advance_system.adapters.upstox.transport import (
    HeartbeatLoop,
    ReconnectPolicy,
    UpstoxTransport,
    UpstoxWebSocketClient,
)
from advance_system.ingestion.adapters import Instrument


class FakeTransport:
    attempts = 0

    def __init__(self) -> None:
        self.connected = False
        self.closed = False
        self.subscribed = False

    async def connect(self, *, access_token: str) -> None:
        FakeTransport.attempts += 1
        if FakeTransport.attempts == 1:
            raise ConnectionError("temporary outage")
        self.connected = True

    async def subscribe(self, *, instruments: Sequence[Instrument]) -> None:
        self.subscribed = True

    async def receive(self) -> AsyncIterator[UpstoxQuote]:
        yield UpstoxQuote("NSE_EQ|TEST", datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc), Decimal("100"))

    async def ping(self) -> None:
        pass

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_reconnect_policy_retries_then_streams():
    FakeTransport.attempts = 0
    created = []

    def factory() -> UpstoxTransport:
        item = FakeTransport()
        created.append(item)
        return item

    client = UpstoxWebSocketClient(factory, reconnect=ReconnectPolicy(initial_delay=0, max_delay=0, max_attempts=2))
    instrument = Instrument("NSE_EQ|TEST", "NSE", "TEST", "EQUITY")
    quotes = []
    async for quote in client.stream_quotes([instrument], "test-token"):
        quotes.append(quote)
        await client.close()

    assert len(quotes) == 1
    assert FakeTransport.attempts == 2
    assert created[0].closed
    assert created[1].subscribed


def test_reconnect_policy_is_bounded():
    policy = ReconnectPolicy(initial_delay=1, max_delay=5, multiplier=2)
    assert [policy.delay(i) for i in range(1, 6)] == [1, 2, 4, 5, 5]


@pytest.mark.asyncio
async def test_heartbeat_loop_pings_at_interval():
    stop = asyncio.Event()
    calls = 0

    async def ping() -> None:
        nonlocal calls
        calls += 1
        stop.set()

    await HeartbeatLoop(ping, timedelta(milliseconds=1)).run(stop)
    assert calls == 1
