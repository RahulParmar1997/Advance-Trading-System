# -*- coding: utf-8 -*-
# Vendored schema-compatible Upstox V3 protobuf boundary.
# Schema source: upstox/upstox-python MarketDataFeedV3.proto
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf.internal import builder as _builder
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2

_PACKAGE = "com.upstox.marketdatafeederv3udapi.rpc.proto"
_sym_db = _symbol_database.Default()


def _message(file_proto, name):
    return file_proto.message_type.add(name=name)


def _field(message, name, number, field_type, *, label=1, type_name=None, oneof_index=None):
    item = message.field.add(name=name, number=number, type=field_type, label=label)
    if type_name is not None:
        item.type_name = type_name
    if oneof_index is not None:
        item.oneof_index = oneof_index
    return item


def _map_entry(parent, name, value_type, value_type_name):
    nested = parent.nested_type.add(name=name)
    nested.options.map_entry = True
    _field(nested, "key", 1, 9)
    _field(nested, "value", 2, value_type, type_name=value_type_name)
    return nested


def _build_file_descriptor():
    file_proto = _descriptor_pb2.FileDescriptorProto(
        name="MarketDataFeedV3.proto",
        package=_PACKAGE,
        syntax="proto3",
    )
    file_proto.dependency.append("google/protobuf/wrappers.proto")

    message = _message(file_proto, "LTPC")
    _field(message, "ltp", 1, 1)
    _field(message, "ltt", 2, 3)
    _field(message, "ltq", 3, 3)
    _field(message, "cp", 4, 1)
    _field(message, "iep", 5, 11, type_name=".google.protobuf.DoubleValue")

    message = _message(file_proto, "MarketLevel")
    _field(message, "bidAskQuote", 1, 11, label=3, type_name=f".{_PACKAGE}.Quote")

    message = _message(file_proto, "MarketOHLC")
    _field(message, "ohlc", 1, 11, label=3, type_name=f".{_PACKAGE}.OHLC")

    message = _message(file_proto, "Quote")
    _field(message, "bidQ", 1, 3)
    _field(message, "bidP", 2, 1)
    _field(message, "askQ", 3, 3)
    _field(message, "askP", 4, 1)

    message = _message(file_proto, "OptionGreeks")
    for number, name in enumerate(("delta", "theta", "gamma", "vega", "rho"), 1):
        _field(message, name, number, 1)

    message = _message(file_proto, "OHLC")
    _field(message, "interval", 1, 9)
    for number, name in enumerate(("open", "high", "low", "close"), 2):
        _field(message, name, number, 1)
    _field(message, "vol", 6, 3)
    _field(message, "ts", 7, 3)

    enum = file_proto.enum_type.add(name="Type")
    for name, number in (("initial_feed", 0), ("live_feed", 1), ("market_info", 2)):
        enum.value.add(name=name, number=number)

    message = _message(file_proto, "MarketFullFeed")
    for number, name, type_name in (
        (1, "ltpc", "LTPC"),
        (2, "marketLevel", "MarketLevel"),
        (3, "optionGreeks", "OptionGreeks"),
        (4, "marketOHLC", "MarketOHLC"),
    ):
        _field(message, name, number, 11, type_name=f".{_PACKAGE}.{type_name}")
    for number, name, field_type in (
        (5, "atp", 1), (6, "vtt", 3), (7, "oi", 1), (8, "iv", 1),
        (9, "tbq", 1), (10, "tsq", 1), (11, "iep", 1), (12, "rp", 1),
        (13, "ieq", 3), (14, "iiqTotal", 3), (15, "iiqM", 3), (16, "casEligible", 8),
    ):
        _field(message, name, number, field_type)

    message = _message(file_proto, "IndexFullFeed")
    _field(message, "ltpc", 1, 11, type_name=f".{_PACKAGE}.LTPC")
    _field(message, "marketOHLC", 2, 11, type_name=f".{_PACKAGE}.MarketOHLC")

    message = _message(file_proto, "FullFeed")
    message.oneof_decl.add(name="FullFeedUnion")
    _field(message, "marketFF", 1, 11, type_name=f".{_PACKAGE}.MarketFullFeed", oneof_index=0)
    _field(message, "indexFF", 2, 11, type_name=f".{_PACKAGE}.IndexFullFeed", oneof_index=0)

    message = _message(file_proto, "FirstLevelWithGreeks")
    _field(message, "ltpc", 1, 11, type_name=f".{_PACKAGE}.LTPC")
    _field(message, "firstDepth", 2, 11, type_name=f".{_PACKAGE}.Quote")
    _field(message, "optionGreeks", 3, 11, type_name=f".{_PACKAGE}.OptionGreeks")
    _field(message, "vtt", 4, 3)
    _field(message, "oi", 5, 1)
    _field(message, "iv", 6, 1)

    message = _message(file_proto, "Feed")
    message.oneof_decl.add(name="FeedUnion")
    _field(message, "ltpc", 1, 11, type_name=f".{_PACKAGE}.LTPC", oneof_index=0)
    _field(message, "fullFeed", 2, 11, type_name=f".{_PACKAGE}.FullFeed", oneof_index=0)
    _field(message, "firstLevelWithGreeks", 3, 11, type_name=f".{_PACKAGE}.FirstLevelWithGreeks", oneof_index=0)
    _field(message, "requestMode", 4, 14, type_name=f".{_PACKAGE}.RequestMode")

    enum = file_proto.enum_type.add(name="RequestMode")
    for name, number in (("ltpc", 0), ("full_d5", 1), ("option_greeks", 2), ("full_d30", 3)):
        enum.value.add(name=name, number=number)

    enum = file_proto.enum_type.add(name="MarketStatus")
    for name, number in (
        ("PRE_OPEN_START", 0), ("PRE_OPEN_END", 1), ("NORMAL_OPEN", 2),
        ("NORMAL_CLOSE", 3), ("CLOSING_START", 4), ("CLOSING_END", 5),
    ):
        enum.value.add(name=name, number=number)

    message = _message(file_proto, "StatusInfo")
    _field(message, "status", 1, 9)
    _field(message, "updatedTime", 2, 3)

    message = _message(file_proto, "MarketInfo")
    _map_entry(message, "SegmentStatusEntry", 14, f".{_PACKAGE}.MarketStatus")
    _map_entry(message, "CasMarketStatusEntry", 11, f".{_PACKAGE}.StatusInfo")
    _map_entry(message, "PreOpenSessionStatusEntry", 11, f".{_PACKAGE}.StatusInfo")
    _field(message, "segmentStatus", 1, 11, label=3, type_name=f".{_PACKAGE}.MarketInfo.SegmentStatusEntry")
    _field(message, "casMarketStatus", 2, 11, label=3, type_name=f".{_PACKAGE}.MarketInfo.CasMarketStatusEntry")
    _field(message, "preOpenSessionStatus", 3, 11, label=3, type_name=f".{_PACKAGE}.MarketInfo.PreOpenSessionStatusEntry")

    message = _message(file_proto, "FeedResponse")
    _map_entry(message, "FeedsEntry", 11, f".{_PACKAGE}.Feed")
    _field(message, "type", 1, 14, type_name=f".{_PACKAGE}.Type")
    _field(message, "feeds", 2, 11, label=3, type_name=f".{_PACKAGE}.FeedResponse.FeedsEntry")
    _field(message, "currentTs", 3, 3)
    _field(message, "marketInfo", 4, 11, type_name=f".{_PACKAGE}.MarketInfo")
    return file_proto


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(_build_file_descriptor().SerializeToString())
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "MarketDataFeedV3_pb2", globals())

__all__ = [
    "LTPC", "MarketLevel", "MarketOHLC", "Quote", "OptionGreeks", "OHLC",
    "MarketFullFeed", "IndexFullFeed", "FullFeed", "FirstLevelWithGreeks", "Feed",
    "StatusInfo", "MarketInfo", "FeedResponse", "Type", "RequestMode", "MarketStatus",
]
