import pytest

from advance_system.adapters.upstox.market_status import UpstoxMarketStatusConfig, UpstoxMarketStatusSource


class FakeHttp:
    def __init__(self, payload: bytes):
        self.payload = payload
        self.calls = []

    async def get(self, *, url, access_token, timeout_seconds):
        self.calls.append((url, access_token, timeout_seconds))
        return self.payload


@pytest.mark.asyncio
async def test_market_status_source_maps_exchange_status_and_cas():
    client = FakeHttp(
        b'{"status":"success","data":{"exchange":"NSE","status":"NORMAL_OPEN","last_updated":1705549500000,"cas_eligible_status":{"status":"CTS_CLOSE","last_updated":1705570500000}}}'
    )
    source = UpstoxMarketStatusSource(UpstoxMarketStatusConfig(), client)
    result = await source.fetch(exchange="nse", access_token="token")
    assert result.exchange == "NSE"
    assert result.status == "NORMAL_OPEN"
    assert result.last_updated_ms == 1705549500000
    assert result.cas_status == "CTS_CLOSE"
    assert client.calls[0][0].endswith("/market/status/NSE")


@pytest.mark.asyncio
async def test_market_status_source_rejects_invalid_response():
    client = FakeHttp(b'{"status":"error","data":{}}')
    source = UpstoxMarketStatusSource(UpstoxMarketStatusConfig(), client)
    with pytest.raises(ValueError, match="not successful"):
        await source.fetch(exchange="NSE", access_token="token")


@pytest.mark.asyncio
async def test_market_status_source_rejects_exchange_mismatch():
    client = FakeHttp(b'{"status":"success","data":{"exchange":"BSE","status":"NORMAL_OPEN","last_updated":1}}')
    source = UpstoxMarketStatusSource(UpstoxMarketStatusConfig(), client)
    with pytest.raises(ValueError, match="identity"):
        await source.fetch(exchange="NSE", access_token="token")


def test_market_status_config_requires_https():
    with pytest.raises(ValueError, match="HTTPS"):
        UpstoxMarketStatusConfig(base_url="http://localhost")
