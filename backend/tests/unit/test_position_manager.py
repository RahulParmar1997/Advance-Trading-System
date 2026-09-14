from datetime import datetime, timezone
from decimal import Decimal

import pytest

from advance_system.journal.audit import AuditEvent, InMemoryAuditJournal
from advance_system.portfolio.manager import PositionManager
from advance_system.reconciliation.contracts import BrokerFill, FillSide, BrokerOrderSnapshot, ReconciliationEngine


NOW = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)


def fill(fill_id: str, side: FillSide, quantity: int, price: str) -> BrokerFill:
    return BrokerFill(fill_id, "o-1", "NSE_EQ|TEST", side, quantity, Decimal(price), NOW)


def test_position_manager_applies_buy_and_sell_and_journals() -> None:
    journal = InMemoryAuditJournal()
    manager = PositionManager(journal=journal)
    manager.apply_fill(fill("f-1", FillSide.BUY, 10, "100"))
    update = manager.apply_fill(fill("f-2", FillSide.SELL, 4, "105"))
    assert update.position.quantity == 6
    assert update.position.realized_pnl == Decimal("20")
    assert len(journal.events()) == 2
    assert journal.events()[-1].event_type == "POSITION_UPDATED"


def test_duplicate_fill_is_rejected() -> None:
    manager = PositionManager()
    manager.apply_fill(fill("f-1", FillSide.BUY, 10, "100"))
    with pytest.raises(ValueError, match="duplicate fill_id"):
        manager.apply_fill(fill("f-1", FillSide.BUY, 10, "100"))


def test_reconciliation_detects_quantity_mismatch() -> None:
    result = ReconciliationEngine().reconcile(
        order_id="o-1",
        canonical_filled=8,
        broker=BrokerOrderSnapshot("o-1", "PARTIALLY_FILLED", 7),
    )
    assert result.matched is False
    assert result.reason == "filled quantity mismatch"


def test_journal_is_append_only_and_ids_are_unique() -> None:
    journal = InMemoryAuditJournal()
    event = AuditEvent("e-1", NOW, "TEST", "entity", {})
    journal.append(event)
    with pytest.raises(ValueError, match="duplicate event_id"):
        journal.append(event)
