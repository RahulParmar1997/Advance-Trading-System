from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Protocol

from advance_system.adapters.upstox.market_data import UpstoxQuote


class FeedDecodeError(ValueError):
    pass


class ProtobufFeedDecoder(Protocol):
    """Adapter for the generated Upstox V3 protobuf FeedResponse type."""

    def decode(self, payload: bytes) -> Any:
        ...


@dataclass(frozen=True, slots=True)
class DecodedFeed:
    """Small broker-neutral representation used before RawQuote normalization."""

    instrument: str
    last_price: Decimal
    timestamp: datetime
    volume: int | None = None
    bid: Decimal | None = None
    ask: Decimal | None = None


class UpstoxFeedMapper:
    """Maps decoded V3 feed structures into deterministic UpstoxQuote values.

    The protobuf-generated class is intentionally injected. This keeps generated
    broker code and protobuf runtime concerns outside the domain and makes tests
    deterministic without requiring a live Upstox connection.
    """

    def map_message(self, message: Any) -> list[UpstoxQuote]:
        feeds = _read(message, "feeds")
        if feeds is None:
            return []
        current_ts = _to_millis(_read(message, "currentTs"))
        result: list[UpstoxQuote] = []
        for instrument, feed in _items(feeds):
            ltpc = _first_present(feed, "ltpc", "firstLevelWithGreeks.ltpc", "fullFeed.marketFF.ltpc", "ff.indexFF.ltpc")
            if ltpc is None:
                continue
            price = _decimal(_read(ltpc, "ltp"), "ltp")
            ltt = _read(ltpc, "ltt")
            timestamp = datetime.fromtimestamp((_to_millis(ltt) if ltt is not None else current_ts) / 1000, tz=timezone.utc)
            bid_quote = _first_bid_ask(feed)
            result.append(
                UpstoxQuote(
                    instrument=instrument,
                    timestamp=timestamp,
                    last_price=price,
                    bid=bid_quote[0] if bid_quote else None,
                    ask=bid_quote[1] if bid_quote else None,
                    volume=_extract_volume(feed),
                )
            )
        return result


def _read(value: Any, name: str) -> Any:
    if value is None:
        return None
    if "." in name:
        current = value
        for part in name.split("."):
            current = _read(current, part)
            if current is None:
                return None
        return current
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name, None)


def _first_present(value: Any, *names: str) -> Any:
    for name in names:
        found = _read(value, name)
        if found is not None:
            return found
    return None


def _items(value: Any):
    if hasattr(value, "items"):
        return value.items()
    return ((key, getattr(value, key)) for key in value.keys())


def _decimal(value: Any, field: str) -> Decimal:
    if value is None:
        raise FeedDecodeError(f"missing {field}")
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise FeedDecodeError(f"invalid {field}") from exc
    if result <= 0:
        raise FeedDecodeError(f"{field} must be positive")
    return result


def _to_millis(value: Any) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise FeedDecodeError("invalid timestamp") from exc
    return result


def _first_bid_ask(feed: Any) -> tuple[Decimal, Decimal] | None:
    quote = _first_present(feed, "firstLevelWithGreeks.bidAskQuote", "fullFeed.marketFF.marketLevel.bidAskQuote", "marketLevel.bidAskQuote")
    if quote is None:
        return None
    if isinstance(quote, (list, tuple)):
        quote = quote[0] if quote else None
    if quote is None:
        return None
    bid = _read(quote, "bp")
    ask = _read(quote, "ap")
    if bid is None or ask is None:
        return None
    return Decimal(str(bid)), Decimal(str(ask))


def _extract_volume(feed: Any) -> int | None:
    value = _first_present(feed, "fullFeed.marketFF.vtt", "fullFeed.marketFF.eFeedDetails.vtt", "eFeedDetails.vtt")
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise FeedDecodeError("invalid volume") from exc
