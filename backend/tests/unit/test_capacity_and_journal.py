from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.domain.market_status import MarketStatus
from advance_system.journal.audit import AuditEvent
from advance_system.journal.durable import JsonlAuditJournal
from advance_system.risk.engine import RiskContext, RiskEngine, RiskPolicy, RiskSnapshot


class Opportunity:
    risk_reward = Decimal("2")


NOW = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)


def context(**kwargs) -> RiskContext:
    values = dict(
        now=NOW,
        market_open=True,
        last_market_data_at=NOW,
        snapshot=RiskSnapshot(available_liquidity=Decimal("100000")),
        order_notional=Decimal("10000"),
        estimated_market_volume=Decimal("100000"),
        market_status=MarketStatus("NSE", "NORMAL_OPEN", NOW),
        expected_exchange="NSE",
    )
    values.update(kwargs)
    return RiskContext(**values)


def policy() -> RiskPolicy:
    return RiskPolicy(
        max_daily_loss=Decimal("100000"), max_strategy_loss=Decimal("50000"),
        max_symbol_exposure=Decimal("100000"), max_portfolio_exposure=Decimal("500000"),
        max_concurrent_trades=10, max_leverage=Decimal("5"), max_slippage_bps=Decimal("25"),
        max_data_age_seconds=30, min_risk_reward=Decimal("1"), max_order_notional=Decimal("50000"),
        max_participation_rate=Decimal("0.25"),
    )


def test_capacity_checks_allow_valid_order() -> None:
    decision = RiskEngine(policy()).check(Opportunity(), context())
    assert decision.allowed
    assert "capacity" in decision.checks


def test_capacity_rejects_insufficient_liquidity() -> None:
    decision = RiskEngine(policy()).check(
        Opportunity(), context(snapshot=RiskSnapshot(available_liquidity=Decimal("9999")))
    )
    assert decision.reason == "insufficient available liquidity"


def test_capacity_rejects_excess_participation() -> None:
    decision = RiskEngine(policy()).check(
        Opportunity(), context(estimated_market_volume=Decimal("30000"))
    )
    assert decision.reason == "market participation limit exceeded"


def test_jsonl_journal_persists_and_rejects_duplicates(tmp_path) -> None:
    journal = JsonlAuditJournal(tmp_path / "audit.jsonl")
    event = AuditEvent("e-1", NOW, "ORDER", "o-1", {"state": "FILLED"})
    journal.append(event)
    assert '"event_id":"e-1"' in (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate event_id"):
        journal.append(event)
