from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from advance_system.journal.audit import AuditEvent, InMemoryAuditJournal
from advance_system.portfolio.positions import Position, PositionBook
from advance_system.reconciliation.contracts import BrokerFill


@dataclass(frozen=True, slots=True)
class PositionUpdate:
    fill_id: str
    position: Position


class PositionManager:
    """Applies validated broker/PAPER fills once and journals every position change."""

    def __init__(self, positions: PositionBook | None = None, journal: InMemoryAuditJournal | None = None) -> None:
        self.positions = positions or PositionBook()
        self.journal = journal or InMemoryAuditJournal()
        self._processed_fills: set[str] = set()

    def apply_fill(self, fill: BrokerFill) -> PositionUpdate:
        fill.validate()
        if fill.fill_id in self._processed_fills:
            raise ValueError("duplicate fill_id")
        signed_quantity = fill.quantity if fill.side.value == "BUY" else -fill.quantity
        position = self.positions.apply_fill(fill.instrument, signed_quantity, fill.price)
        self._processed_fills.add(fill.fill_id)
        self.journal.append(AuditEvent(
            event_id=f"position:{fill.fill_id}",
            timestamp=fill.timestamp,
            event_type="POSITION_UPDATED",
            entity_id=fill.instrument,
            payload={
                "fill_id": fill.fill_id,
                "quantity": str(fill.quantity),
                "price": str(fill.price),
                "position_quantity": str(position.quantity),
                "realized_pnl": str(position.realized_pnl),
            },
        ))
        return PositionUpdate(fill.fill_id, position)
