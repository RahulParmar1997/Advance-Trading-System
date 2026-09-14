# -*- coding: utf-8 -*-
# Generated-compatible vendored artifact for the pinned Upstox V3 schema.
# Source: MarketDataFeedV3.proto (Upstox official SDK)
# Source blob SHA: f2da2a585579a42c16521a67274bca4c91186396
# Upstream generated code was produced with protobuf Python 4.25.4.
"""Vendored Upstox MarketDataFeedV3 protobuf module."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf.internal import builder as _builder
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2

_PACKAGE = "com.upstox.marketdatafeederv3udapi.rpc.proto"
_FILE = "MarketDataFeedV3.proto"


def _field(message, name, number, field_type, *, label=1, type_name=None, oneof_index=None):
    field = message.field.add(name=name, number=number, type=field_type, label=label)
    if type_name is not None:
        field.type_name = type_name
    if oneof_index is not None:
        field.oneof_index = oneof_index
    return field


def _message(file_proto, name):
    return file_proto.message_type.add(name=name)


def _map_entry(parent, name, key_type, value_type, value_type_name=None):
    nested = parent.nested_type.add(name=name)
    nested.options.map_entry = True
    _field(nested, "key", 1, key_type)
    _field(nested, "value", 2, value_type, type_name=value_type_name)
    return nested


def _build_file_descriptor():
    file_proto = _descriptor_pb2.FileDescriptorProto(
        name=_FILE,
        package=_PACKAGE,
        syntax="proto3",
    )
    file_proto.dependency.append("google/protobuf/wrappers.proto")

    ltpc = _message(file_proto, "LTPC")
    _field(ltpc, "ltp", 1, 1)
    _field(ltpc, "ltt", 2, 3)
    _field(ltpc, "ltq", 3, 3)
    _field(ltpc, "cp", 4, 1)
    _field(ltpc, "iep", 5, 11, type_name=".google.protobuf.DoubleValue")

    market_level = _message(file_proto, "MarketLevel")
    _field(market_level, "bidAskQuote", 1, 11, label=3, type_name=f".{_PACKAGE}.Quote")

    market_ohlc = _message(file_proto, "MarketOHLC")
    _field(market_ohlc, "ohlc", 1, 11, label=3, type_name=f".{_PACKAGE}.OHLC")

    quote = _message(file_proto, "Quote")
    _field(quote, "bidQ", 1, 3)
    _field(quote, "bidP", 2, 1)
    _field(quote, "askQ", 3, 3)
    _field(quote, "askP", 4, 1)

    greeks = _message(file_proto, "OptionGreeks")
    for number, name in enumerate(("delta", "theta", "gamma", "vega", "rho"), 1):
        _field(greeks, name, number, 1)

    ohlc = _message(file_proto, "OHLC")
    _field(ohlc, "interval", 1, 9)
    for number, name in enumerate(("open", "high", "low", "close"), 2):
        _field(ohlc, name, number, 1)
    _field(ohlc, "vol", 6, 3)
    _field(ohlc, "ts", 7, 3)

    enum = file_proto.enum_type.add(name="Type")
    for name, number in (("initial_feed", 0), ("live_feed", 1), ("market_info", 2)):
        enum.value.add(name=name, number=number)

    full = _message(file_proto, "MarketFullFeed")
    for number, name, type_name in (
        (1, "ltpc", "LTPC"),
        (2, "marketLevel", "MarketLevel"),
        (3, "optionGreeks", "OptionGreeks"),
        (4, "marketOHLC", "MarketOHLC"),
    ):
        _field(full, name, number, 11, type_name=f".{_PACKAGE}.{type_name}")
    _field(full, "atp", 5, 1)
    _field(full, "vtt", 6, 3)
    _field(full, "oi", 7, 1)
    _field(full, "iv", 8, 1)
    _field(full, "tbq", 9, 1)
    _field(full, "tsq", 10, 1)
    _field(full, "iep", 11, 1)
    _field(full, "rp", 12, 1)
    _field(full, "ieq", 13, 3)
    _field(full, "iiqTotal", 14, 3)
    _field(full, "iiqM", 15, 3)
    _field(full, "casEligible", 16, 8)

    index = _message(file_proto, "IndexFullFeed")
    _field(index, "ltpc", 1, 11, type_name=f".{_PACKAGE}.LTPC")
    _field(index, "marketOHLC", 2, 11, type_name=f".{_PACKAGE}.MarketOHLC")

    full_feed = _message(file_proto, "FullFeed")
    full_feed.oneof_decl.add(name="FullFeedUnion")
    _field(full_feed, "marketFF", 1, 11, type_name=f".{_PACKAGE}.MarketFullFeed", oneof_index=0)
    _field(full_feed, "indexFF", 2, 11, type_name=f".{_PACKAGE}.IndexFullFeed", oneof_index=0)

    first = _message(file_proto, "FirstLevelWithGreeks")
    _field(first, "ltpc", 1, 11, type_name=f".{_PACKAGE}.LTPC")
    _field(first, "firstDepth", 2, 11, type_name=f".{_PACKAGE}.Quote")
    _field(first, "optionGreeks", 3, 11, type_name=f".{_PACKAGE}.OptionGreeks")
    _field(first, "vtt", 4, 3)
    _field(first, "oi", 5, 1)
    _field(first, "iv", 6, 1)

    feed = _message(file_proto, "Feed")
    feed.oneof_decl.add(name="FeedUnion")
    _field(feed, "ltpc", 1, 11, type_name=f".{_PACKAGE}.LTPC", oneof_index=0)
    _field(feed, "fullFeed", 2, 11, type_name=f".{_PACKAGE}.FullFeed", oneof_index=0)
    _field(feed, "firstLevelWithGreeks", 3, 11, type_name=f".{_PACKAGE}.FirstLevelWithGreeks", oneof_index=0)

    request_mode = file_proto.enum_type.add(name="RequestMode")
    for name, number in (("ltpc", 0), ("full_d5", 1), ("option_greeks", 2), ("full_d30", 3)):
        request_mode.value.add(name=name, number=number)
    _field(feed, "requestMode", 4, 14, type_name=f".{_PACKAGE}.RequestMode")

    market_status = file_proto.enum_type.add(name="MarketStatus")
    for name, number in (("PRE_OPEN_START", 0), ("PRE_OPEN_END", 1), ("NORMAL_OPEN", 2), ("NORMAL_CLOSE", 3), ("CLOSING_START", 4), ("CLOSING_END", 5)):
        market_status.value.add(name=name, number=number)

    status = _message(file_proto, "StatusInfo")
    _field(status, "status", 1, 9)
    _field(status, "updatedTime", 2, 3)

    market_info = _message(file_proto, "MarketInfo")
    _map_entry(market_info, "SegmentStatusEntry", 9, 14, f".{_PACKAGE}.MarketStatus")
    _map_entry(market_info, "CasMarketStatusEntry", 9, 11, f".{_PACKAGE}.StatusInfo")
    _map_entry(market_info, "PreOpenSessionStatusEntry", 9, 11, f".{_PACKAGE}.StatusInfo")
    _field(market_info, "segmentStatus", 1, 11, label=3, type_name=f".{_PACKAGE}.MarketInfo.SegmentStatusEntry")
    _field(market_info, "casMarketStatus", 2, 11, label=3, type_name=f".{_PACKAGE}.MarketInfo.CasMarketStatusEntry")
    _field(market_info, "preOpenSessionStatus", 3, 11, label=3, type_name=f".{_PACKAGE}.MarketInfo.PreOpenSessionStatusEntry")

    response = _message(file_proto, "FeedResponse")
    _map_entry(response, "FeedsEntry", 9, 11, f".{_PACKAGE}.Feed")
    _field(response, "type", 1, 14, type_name=f".{_PACKAGE}.Type")
    _field(response, "feeds", 2, 11, label=3, type_name=f".{_PACKAGE}.FeedResponse.FeedsEntry")
    _field(response, "currentTs", 3, 3)
    _field(response, "marketInfo", 4, 11, type_name=f".{_PACKAGE}.MarketInfo")
    return file_proto


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(_build_file_descriptor().SerializeToString())
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "MarketDataFeedV3_pb2", _globals)

__all__ = [
    "LTPC", "MarketLevel", "MarketOHLC", "Quote", "OptionGreeks", "OHLC",
    "MarketFullFeed", "IndexFullFeed", "FullFeed", "FirstLevelWithGreeks", "Feed",
    "StatusInfo", "MarketInfo", "FeedResponse", "Type", "RequestMode", "MarketStatus",
]
