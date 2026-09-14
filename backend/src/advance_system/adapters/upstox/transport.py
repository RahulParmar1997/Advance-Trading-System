from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol

from advance_system.adapters.upstox.market_data import UpstoxQuote, UpstoxMarketDataClient
from advance_system.ingestion.adapters import Instrument


class UpstoxTransport(Protocol):
    async def connect(self, *, access_token: str) -> None:
        ...

    async def subscribe(self, *, instruments: Sequence[Instrument]) -> None:
        ...

    async def receive(self) -> AsyncIterator[UpstoxQuote]:
        ...

    async def ping(self) -> None:
        ...

    async def close(self) -> None:
        ...


@dataclass(frozen=True, slots=True)
class ReconnectPolicy:
    initial_delay: float = 1.0
    max_delay: float = 30.0
    multiplier: float = 2.0
    max_attempts: int | None = None

    def delay(self, attempt: int) -> float:
        if attempt < 1:
            raise ValueError("attempt must be >= 1")
        return min(self.max_delay, self.initial_delay * self.multiplier ** (attempt - 1))


class UpstoxWebSocketClient(UpstoxMarketDataClient):
    """Transport orchestrator; concrete WebSocket library remains injectable."""

    def __init__(
        self,
        transport_factory: Callable[[], UpstoxTransport],
        *,
        reconnect: ReconnectPolicy | None = None,
        heartbeat_interval: timedelta = timedelta(seconds=15),
    ) -> None:
        if heartbeat_interval <= timedelta(0):
            raise ValueError("heartbeat_interval must be positive")
        self.transport_factory = transport_factory
        self.reconnect = reconnect or ReconnectPolicy()
        self.heartbeat_interval = heartbeat_interval
        self._transport: UpstoxTransport | None = None
        self._closed = False

    async def stream_quotes(self, instruments: Sequence[Instrument], access_token: str) -> AsyncIterator[UpstoxQuote]:
        attempt = 0
        while not self._closed:
            transport = self.transport_factory()
            self._transport = transport
            try:
                await transport.connect(access_token=access_token)
                await transport.subscribe(instruments=instruments)
                attempt = 0
                async for quote in transport.receive():
                    yield quote
                if self._closed:
                    break
                raise ConnectionError("Upstox stream ended")
            except asyncio.CancelledError:
                raise
            except Exception:
                attempt += 1
                if self.reconnect.max_attempts is not None and attempt > self.reconnect.max_attempts:
                    raise
                await asyncio.sleep(self.reconnect.delay(attempt))
            finally:
                await transport.close()
                if self._transport is transport:
                    self._transport = None

    async def close(self) -> None:
        self._closed = True
        if self._transport is not None:
            await self._transport.close()


class HeartbeatLoop:
    """Reusable heartbeat policy; concrete ping implementation is injected."""

    def __init__(self, ping: Callable[[], Awaitable[None]], interval: timedelta) -> None:
        if interval <= timedelta(0):
            raise ValueError("interval must be positive")
        self.ping = ping
        self.interval = interval

    async def run(self, stop: asyncio.Event) -> None:
        while not stop.is_set():
            try:
                await asyncio.wait_for(stop.wait(), timeout=self.interval.total_seconds())
            except asyncio.TimeoutError:
                await self.ping()
