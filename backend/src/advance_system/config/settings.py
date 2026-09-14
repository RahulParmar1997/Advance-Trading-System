from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UpstoxSettings:
    client_id: str
    client_secret: str
    redirect_uri: str
    token_url: str = "https://api.upstox.com/v2/login/authorization/token"
    market_data_authorize_url: str = "https://api.upstox.com/v3/feed/market-data-feed/authorize"

    @classmethod
    def from_environment(cls) -> "UpstoxSettings":
        values = {
            "client_id": os.getenv("UPSTOX_CLIENT_ID"),
            "client_secret": os.getenv("UPSTOX_CLIENT_SECRET"),
            "redirect_uri": os.getenv("UPSTOX_REDIRECT_URI"),
        }
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise RuntimeError(f"missing required Upstox environment variables: {', '.join(missing)}")
        return cls(**values)  # type: ignore[arg-type]
