import asyncio
import json

import pytest

from advance_system.adapters.upstox.websocket_transport import (
    UpstoxLibraryWebSocketTransport,
    UpstoxWebSocketConfig,
    run_heartbeat,
)


class FakeConnection:
    def __init__(self) -> None:
        self.sent = []
        self.closed = False
        self.pings = 0
        self.messages = []

    async def send(self, data):
        self.sent.append(data)

    async def recv(self):
        return self.messages.pop(0) if self.messages else None

    async def ping(self, data=b""):
        self.pings += 1

    async def close(self):
        self.closed = True


class FakeConnector:
    def __init__(self, connection):
        self.connection = connection
        self.calls = []

    async def connect(self, *, url, headers):
        self.calls.append((url, headers))
        return self.connection


class FakeMapper:
    def map_message(self, message):
        return [message]


class FakeDecoder:
    def decode(self, message):
        return message


@pytest.mark.asyncio
async def test_connect_subscribe_receive_and_close():
    connection = FakeConnection()
    connector = FakeConnector(connection)
    transport = UpstoxLibraryWebSocketTransport(
        connector, FakeMapper(), FakeDecoder(), UpstoxWebSocketConfig("wss://feed.example")
    )
    await transport.connect(access_token="secret-token")
    await transport.subscribe(instruments=[])
    connection.messages.append(b"feed")
    values = [quote async for quote in transport.receive()]
    await transport.close()
    payload = json.loads(connection.sent[0])
    assert values == [b"feed"]
    assert connector.calls == [("wss://feed.example", {"Authorization": "Bearer secret-token"})]
    assert payload["method"] == "sub"
    assert connection.closed is True
    assert "secret-token" not in connection.sent[0]


@pytest.mark.asyncio
async def test_empty_token_is_rejected_before_network_connect():
    connector = FakeConnector(FakeConnection())
    transport = UpstoxLibraryWebSocketTransport(
        connector, FakeMapper(), FakeDecoder(), UpstoxWebSocketConfig("wss://feed.example")
    )
    with pytest.raises(ValueError, match="access token cannot be empty"):
        await transport.connect(access_token=" ")
    assert connector.calls == []


@pytest.mark.asyncio
async def test_operations_require_connection():
    transport = UpstoxLibraryWebSocketTransport(
        FakeConnector(FakeConnection()), FakeMapper(), FakeDecoder(), UpstoxWebSocketConfig("wss://feed.example")
    )
    with pytest.raises(RuntimeError, match="not connected"):
        await transport.ping()
    await transport.close()


@pytest.mark.asyncio
async def test_heartbeat_pings_and_stops_cleanly():
    connection = FakeConnection()
    transport = UpstoxLibraryWebSocketTransport(
        FakeConnector(connection), FakeMapper(), FakeDecoder(), UpstoxWebSocketConfig("wss://feed.example", ping_interval=0.01)
    )
    await transport.connect(access_token="token")
    stop = asyncio.Event()
    task = asyncio.create_task(run_heartbeat(transport, stop))
    await asyncio.sleep(0.03)
    stop.set()
    await asyncio.wait_for(task, timeout=1)
    assert connection.pings >= 1


def test_invalid_websocket_config_is_rejected():
    with pytest.raises(ValueError, match="websocket url cannot be empty"):
        UpstoxWebSocketConfig(" ")
    with pytest.raises(ValueError, match="ping_interval must be positive"):
        UpstoxWebSocketConfig("wss://feed.example", ping_interval=0)
