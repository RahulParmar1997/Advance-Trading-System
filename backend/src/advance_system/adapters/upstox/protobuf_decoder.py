from __future__ import annotations

from typing import Any, Type


class UpstoxProtobufDecoder:
    """Thin wrapper around the generated Upstox V3 protobuf class.

    The generated class is injected so the repository does not vendor generated
    broker code or require a protobuf compiler during application startup.
    """

    def __init__(self, feed_response_type: Type[Any]) -> None:
        self.feed_response_type = feed_response_type

    def decode(self, payload: bytes) -> Any:
        if not isinstance(payload, bytes) or not payload:
            raise ValueError("protobuf payload must be non-empty bytes")
        try:
            return self.feed_response_type.FromString(payload)
        except Exception as exc:
            raise ValueError("invalid Upstox V3 protobuf payload") from exc
