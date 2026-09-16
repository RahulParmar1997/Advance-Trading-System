from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol
from urllib.request import Request, urlopen

from advance_system.domain.market_status import MarketStatus


@dataclass(frozen=True, slots=True)
class UpstoxMarketStatus:
    exchange: str
    status: str
    last_updated_ms: int
    cas_status: str | None = None

    def to_domain(self) -> MarketStatus:
        """Convert the broker response to the validated domain status contract."""
        observed_at = datetime.fromtimestamp(self.last_updated_ms / 1000, tz=timezone.utc)
        result = MarketStatus(
            exchange=self.exchange,
            status=self.status,
            observed_at=observed_at,
            cas_status=self.cas_status,
        )
        result.validate()
        return result


@dataclass(frozen=True, slots=True)
class UpstoxMarketStatusConfig:
    """Configuration for the official Upstox market-status source."""

    base_url: str = "https://api.upstox.com/v2"
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        if not self.base_url.startswith("https://"):
            raise ValueError("market status base URL must use HTTPS")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


class MarketStatusHttpClient(Protocol):
    async def get(self, *, url: str, access_token: str, timeout_seconds: float) -> bytes:
        ...


class UrllibMarketStatusHttpClient:
    async def get(self, *, url: str, access_token: str, timeout_seconds: float) -> bytes:
        import asyncio

        def fetch() -> bytes:
            request = Request(
                url,
                headers={"Accept": "application/json", "Authorization": f"Bearer {access_token}"},
                method="GET",
            )
            with urlopen(request, timeout=timeout_seconds) as response:
                return response.read()

        return await asyncio.to_thread(fetch)


class UpstoxMarketStatusSource:
    """Fetch authoritative exchange status while keeping HTTP injectable for tests."""

    def __init__(self, config: UpstoxMarketStatusConfig, http_client: MarketStatusHttpClient) -> None:
        self._config = config
        self._http_client = http_client

    async def fetch(self, *, exchange: str, access_token: str) -> UpstoxMarketStatus:
        exchange = exchange.strip().upper()
        if not exchange:
            raise ValueError("exchange is required")
        if not access_token.strip():
            raise ValueError("access token is required")
        payload = await self._http_client.get(
            url=f"{self._config.base_url.rstrip('/')}/market/status/{exchange}",
            access_token=access_token,
            timeout_seconds=self._config.timeout_seconds,
        )
        return self._parse(payload, exchange)

    @staticmethod
    def _parse(payload: bytes, requested_exchange: str) -> UpstoxMarketStatus:
        try:
            decoded: Any = json.loads(payload)
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid market status JSON") from exc
        if not isinstance(decoded, dict) or decoded.get("status") != "success":
            raise ValueError("market status response is not successful")
        data = decoded.get("data")
        if not isinstance(data, dict):
            raise ValueError("market status response data is invalid")
        exchange = data.get("exchange")
        status = data.get("status")
        last_updated = data.get("last_updated")
        if exchange != requested_exchange or not isinstance(status, str) or not status.strip():
            raise ValueError("market status response identity is invalid")
        if isinstance(last_updated, bool) or not isinstance(last_updated, int) or last_updated < 0:
            raise ValueError("market status last_updated must be a non-negative integer")
        cas = data.get("cas_eligible_status")
        cas_status = None
        if cas is not None:
            if not isinstance(cas, dict) or not isinstance(cas.get("status"), str):
                raise ValueError("invalid CAS market status")
            cas_status = cas["status"]
        return UpstoxMarketStatus(exchange, status, last_updated, cas_status)
