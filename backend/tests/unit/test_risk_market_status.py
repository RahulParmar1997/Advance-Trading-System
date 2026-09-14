from datetime import datetime, timedelta, timezone
from decimal import Decimal

from advance_system.domain.market_status import MarketStatus
from advance_system.risk.engine import RiskContext, RiskEngine, RiskPolicy, RiskSnapshot


class Opportunity:
    risk_reward = Decimal("2")


def make_context(*, status: MarketStatus | None, now: datetime, market_open: bool = True) -> RiskContext:
    return RiskContext(
        now=now,
        market_open=market_open,
        last_market_data_at=now,
        snapshot=RiskSnapshot(
            concurrent_trades=0,
            available_liquidity=Decimal("100000"),
        ),
        order_notional=Decimal("1000"),
        market_status=status,
        expected_exchange="NSE",
    )


def engine() -> RiskEngine:
    return RiskEngine(
        RiskPolicy(
            max_concurrent_trades=5,
            max_leverage=Decimal("5"),
            max_data_age_seconds=10,
        )
    )


def test_fresh_normal_open_status_allows_trade() -> None:
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
    status = MarketStatus("NSE", "NORMAL_OPEN", now - timedelta(seconds=10))

    decision = engine().check(Opportunity(), make_context(status=status, now=now))

    assert decision.allowed is True
    assert "authoritative market status" in decision.checks


def test_missing_authoritative_status_fails_closed() -> None:
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)

    decision = engine().check(Opportunity(), make_context(status=None, now=now))

    assert decision.allowed is False
    assert decision.reason == "authoritative market status unavailable"


def test_stale_market_status_fails_closed() -> None:
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
    status = MarketStatus("NSE", "NORMAL_OPEN", now - timedelta(seconds=61))

    decision = engine().check(Opportunity(), make_context(status=status, now=now))

    assert decision.allowed is False
    assert decision.reason == "market status is stale"


def test_non_open_status_fails_closed() -> None:
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
    status = MarketStatus("NSE", "NORMAL_CLOSE", now - timedelta(seconds=10))

    decision = engine().check(Opportunity(), make_context(status=status, now=now))

    assert decision.allowed is False
    assert decision.reason == "market status is not normal open"


def test_cas_status_does_not_override_non_open_market_status() -> None:
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
    status = MarketStatus("NSE", "NORMAL_CLOSE", now - timedelta(seconds=10), cas_status="CTS_CLOSE")

    decision = engine().check(Opportunity(), make_context(status=status, now=now))

    assert decision.allowed is False
    assert decision.reason == "market status is not normal open"


def test_exchange_mismatch_fails_closed() -> None:
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
    status = MarketStatus("BSE", "NORMAL_OPEN", now - timedelta(seconds=10))

    decision = engine().check(Opportunity(), make_context(status=status, now=now))

    assert decision.allowed is False
    assert decision.reason == "market status exchange mismatch"


def test_market_open_boolean_remains_a_conservative_gate() -> None:
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
    status = MarketStatus("NSE", "NORMAL_OPEN", now - timedelta(seconds=10))

    decision = engine().check(Opportunity(), make_context(status=status, now=now, market_open=False))

    assert decision.allowed is False
    assert decision.reason == "market is closed"
