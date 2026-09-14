from datetime import timezone
from decimal import Decimal

import pytest

from advance_system.adapters.upstox.feed_mapper import FeedDecodeError, UpstoxFeedMapper


def test_maps_ltpc_feed_to_quote():
    message = {
        "type": "live_feed",
        "currentTs": "1740729566039",
        "feeds": {
            "NSE_FO|45450": {
                "ltpc": {
                    "ltp": 219.3,
                    "ltt": "1740729552723",
                    "ltq": "75",
                    "cp": 494.05,
                }
            }
        },
    }

    quote = UpstoxFeedMapper().map_message(message)[0]
    assert quote.instrument == "NSE_FO|45450"
    assert quote.last_price == Decimal("219.3")
    assert quote.timestamp.tzinfo is timezone.utc
    assert quote.bid is None
    assert quote.ask is None


def test_maps_full_feed_bid_ask_and_volume():
    message = {
        "currentTs": "1740729566039",
        "feeds": {
            "NSE_EQ|TEST": {
                "fullFeed": {
                    "marketFF": {
                        "ltpc": {"ltp": 250.5, "ltt": "1740729552723"},
                        "marketLevel": {"bidAskQuote": [{"bp": 250.4, "ap": 250.6}]},
                        "vtt": "1234",
                    }
                }
            }
        },
    }

    quote = UpstoxFeedMapper().map_message(message)[0]
    assert quote.bid == Decimal("250.4")
    assert quote.ask == Decimal("250.6")
    assert quote.volume == 1234


def test_invalid_ltp_is_rejected():
    with pytest.raises(FeedDecodeError, match="ltp"):
        UpstoxFeedMapper().map_message({"feeds": {"NSE_EQ|TEST": {"ltpc": {"ltp": 0}}}})


def test_missing_feeds_is_empty():
    assert UpstoxFeedMapper().map_message({"type": "market_info"}) == []
