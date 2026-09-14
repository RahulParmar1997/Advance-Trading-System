import pytest

from advance_system.adapters.upstox.protobuf_decoder import (
    UPSTOX_V3_PROTO_MODULE,
    UPSTOX_V3_PROTO_PACKAGE,
    UpstoxProtobufDecoder,
    create_upstox_v3_decoder,
    load_generated_feed_response,
)


class FakeFeedResponse:
    @classmethod
    def FromString(cls, payload):
        return {"payload": payload}


def test_decoder_accepts_non_empty_bytes():
    assert UpstoxProtobufDecoder(FakeFeedResponse).decode(b"feed") == {"payload": b"feed"}


def test_decoder_rejects_empty_payload():
    with pytest.raises(ValueError, match="non-empty bytes"):
        UpstoxProtobufDecoder(FakeFeedResponse).decode(b"")


def test_decoder_rejects_non_bytes_payload():
    with pytest.raises(ValueError, match="non-empty bytes"):
        UpstoxProtobufDecoder(FakeFeedResponse).decode("feed")


def test_decoder_hides_parser_error():
    class BrokenFeed:
        @classmethod
        def FromString(cls, payload):
            raise RuntimeError("internal parser detail")

    with pytest.raises(ValueError, match="invalid Upstox V3 protobuf payload"):
        UpstoxProtobufDecoder(BrokenFeed).decode(b"feed")


def test_generated_loader_uses_explicit_pinned_module_boundary():
    assert UPSTOX_V3_PROTO_PACKAGE.endswith("generated")
    assert UPSTOX_V3_PROTO_MODULE == "market_data_feed_v3_pb2"

    with pytest.raises(RuntimeError, match="pinned Upstox V3 protobuf package"):
        load_generated_feed_response()

    with pytest.raises(RuntimeError, match="pinned Upstox V3 protobuf package"):
        create_upstox_v3_decoder()
