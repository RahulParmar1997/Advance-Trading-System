from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from advance_system.adapters.upstox.feed_mapper import UpstoxFeedMapper
from advance_system.adapters.upstox.market_data import UpstoxQuote
from advance_system.ingestion.adapters import Instrument


class WebSocketConnection(Protocol):
    async def send(self, data: bytes | str) -> None: ...
    async def recv(self) -> Any: ...
    async def ping(self, data: bytes = b"") -> Any: ...
    async def close(self) -> None: ...


class WebSocketConnector(Protocol):
    async def connect(self, *, url: str, headers: dict[str, str]) -> WebSocketConnection: ...


@dataclass(frozen=True, slots=True)
class UpstoxWebSocketConfig:
    url: str
    ping_interval: float = 15.0

    def __post_init__(self) -> None:
        if not self.url.strip():
            raise ValueError("websocket url cannot be empty")
        if self.ping_interval <= 0:
            raise ValueError("ping_interval must be positive")


class UpstoxLibraryWebSocketTransport:
    """Concrete Upstox transport; the third-party WebSocket client is injectable."""

    def __init__(self, connector: WebSocketConnector, mapper: UpstoxFeedMapper, config: UpstoxWebSocketConfig) -> None:
        self._connector = connector
        self._mapper = mapper
        self._config = config
        self._connection: WebSocketConnection | None = None

    async def connect(self, *, access_token: str) -> None:
        if not access_token.strip():
            raise ValueError("access token cannot be empty")
        self._connection = await self._connector.connect(
            url=self._config.url,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    async def subscribe(self, *, instruments: Sequence[Instrument]) -> None:
        connection = self._require_connection()
        payload = self._mapper.subscription_payload(instruments)
        await connection.send(payload)

    async def receive(self) -> AsyncIterator[UpstoxQuote]:
        connection = self._require_connection()
        while True:
            message = await connection.recv()
            if message is None:
                return
            if isinstance(message, str):
                message = message.encode("utf-8")
            if not isinstance(message, bytes):
                raise TypeError("websocket message must be bytes or text")
            yield self._mapper.decode(message)

    async def ping(self) -> None:
        connection = self._require_connection()
        pong = await connection.ping()
        if hasattr(pong, "__await__"):
            await pong

    async def close(self) -> None:
        connection, self._connection = self._connection, None
        if connection is not None:
            await connection.close()

    def _require_connection(self) -> WebSocketConnection:
        if self._connection is None:
            raise RuntimeError("websocket is not connected")
        return self._connection


class WebsocketsConnector:
    """Production connector backed by the optional `websockets` package."""

    async def connect(self, *, url: str, headers: dict[str, str]) -> WebSocketConnection:
        try:
            from websockets.asyncio.client import connect
        except ImportError as exc:
            raise RuntimeError("install the websockets optional dependency to use the live transport") from exc
        return await connect(url, additional_headers=headers)


async def run_heartbeat(transport: UpstoxLibraryWebSocketTransport, stop: asyncio.Event) -> None:
    """Run transport heartbeats until shutdown or cancellation."""
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=transport._config.ping_interval)
        except asyncio.TimeoutError:
            await transport.ping()
