"""Stable lowercase import boundary for the vendored Upstox V3 protobuf module."""

from . import MarketDataFeedV3_pb2 as _schema
from .MarketDataFeedV3_pb2 import *  # noqa: F401,F403

initial_feed = _schema.initial_feed
live_feed = _schema.live_feed
market_info = _schema.market_info
PRE_OPEN_START = _schema.PRE_OPEN_START
PRE_OPEN_END = _schema.PRE_OPEN_END
NORMAL_OPEN = _schema.NORMAL_OPEN
NORMAL_CLOSE = _schema.NORMAL_CLOSE
CLOSING_START = _schema.CLOSING_START
CLOSING_END = _schema.CLOSING_END
