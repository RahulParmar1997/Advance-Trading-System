from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Literal


ViewName = Literal["market-state", "scanner", "risk", "portfolio"]


@dataclass(frozen=True, slots=True)
class TerminalViewResponse:
    """Stable read-only terminal contract; unavailable data is never synthesized."""

    schema_version: str
    view: ViewName
    mode: str
    available: bool
    reason: str
    data: object | None = None

    def to_json(self) -> bytes:
        return json.dumps(asdict(self), separators=(",", ":"), sort_keys=True).encode("utf-8")


def unavailable_view(view: ViewName) -> TerminalViewResponse:
    return TerminalViewResponse(
        schema_version="v1",
        view=view,
        mode="PAPER",
        available=False,
        reason="data_feed_not_connected",
        data=None,
    )


VIEW_PATHS: dict[str, ViewName] = {
    "/api/v1/market-state": "market-state",
    "/api/v1/scanner": "scanner",
    "/api/v1/risk": "risk",
    "/api/v1/portfolio": "portfolio",
}
