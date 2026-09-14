from __future__ import annotations

from importlib import import_module
from typing import Any, Type

UPSTOX_V3_PROTO_PACKAGE = "advance_system.adapters.upstox.generated"
UPSTOX_V3_PROTO_MODULE = "market_data_feed_v3_pb2"
UPSTOX_V3_PROTO_VERSION = "v3"


class UpstoxProtobufDecoder:
    """Thin wrapper around the generated Upstox V3 FeedResponse class."""

    def __init__(self, feed_response_type: Type[Any]) -> None:
        self.feed_response_type = feed_response_type

    def decode(self, payload: bytes) -> Any:
        if not isinstance(payload, bytes) or not payload:
            raise ValueError("protobuf payload must be non-empty bytes")
        try:
            return self.feed_response_type.FromString(payload)
        except Exception as exc:
            raise ValueError("invalid Upstox V3 protobuf payload") from exc


def load_generated_feed_response() -> Type[Any]:
    """Load the repository-pinned generated FeedResponse class explicitly."""
    try:
        module = import_module(f"{UPSTOX_V3_PROTO_PACKAGE}.{UPSTOX_V3_PROTO_MODULE}")
        return module.FeedResponse
    except (ImportError, AttributeError) as exc:
        raise RuntimeError("pinned Upstox V3 protobuf package is unavailable") from exc


def create_upstox_v3_decoder() -> UpstoxProtobufDecoder:
    return UpstoxProtobufDecoder(load_generated_feed_response())
