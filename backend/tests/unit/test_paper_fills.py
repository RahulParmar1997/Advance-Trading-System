from decimal import Decimal

from advance_system.execution.paper_fills import PaperFillSimulator
from advance_system.oms.idempotency import PaperOrderGateway
from advance_system.oms.state_machine import OmsOrder, OmsState
from advance_system.portfolio.positions import PositionBook


def test_full_paper_fill_updates_position_and_state() -> None:
    gateway = PaperOrderGateway()
    gateway.submit(OmsOrder("o-1", "NSE_EQ|TEST", 10), client_key="k-1")
    positions = PositionBook()
    fill = PaperFillSimulator(gateway, positions).fill("o-1", Decimal("100"))
    assert fill.quantity == 10
    assert gateway.get("o-1").state is OmsState.FILLED
    position = positions.get("NSE_EQ|TEST")
    assert position.quantity == 10
    assert position.average_price == Decimal("100")


def test_partial_then_full_fill_and_unrealized_pnl() -> None:
    gateway = PaperOrderGateway()
    gateway.submit(OmsOrder("o-2", "NSE_EQ|TEST", 10), client_key="k-2")
    positions = PositionBook()
    simulator = PaperFillSimulator(gateway, positions)
    simulator.fill("o-2", Decimal("100"), quantity=4)
    simulator.fill("o-2", Decimal("102"), quantity=6)
    position = positions.get("NSE_EQ|TEST")
    assert position.quantity == 10
    assert position.average_price == Decimal("101.2")
    assert positions.unrealized_pnl("NSE_EQ|TEST", Decimal("103")) == Decimal("18")


def test_reducing_long_realizes_pnl() -> None:
    positions = PositionBook()
    positions.apply_fill("NSE_EQ|TEST", 10, Decimal("100"))
    position = positions.apply_fill("NSE_EQ|TEST", -4, Decimal("105"))
    assert position.quantity == 6
    assert position.realized_pnl == Decimal("20")
