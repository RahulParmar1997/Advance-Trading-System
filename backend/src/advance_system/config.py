from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv("ENVIRONMENT", "development")
    trading_mode: str = os.getenv("TRADING_MODE", "PAPER")

    @property
    def live_execution_allowed(self) -> bool:
        return self.environment == "production" and self.trading_mode == "LIVE"


settings = Settings()
