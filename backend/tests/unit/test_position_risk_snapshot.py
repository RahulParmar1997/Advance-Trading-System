from decimal import Decimal

import pytest

from advance_system.portfolio.positions import PositionBook


def test_position_book_builds_live_risk_snapshot() -> None:
    book = PositionBook()
    book.apply_fill("NSE_EQ|AAA", 10, Decimal("100"))
    book.apply_fill("NSE_EQ|BBB", -5, Decimal("200"))

    snapshot = book.risk_snapshot(
        {"NSE_EQ|AAA": Decimal("110"), "NSE_EQ|BBB": Decimal("190")},
        daily_pnl=Decimal("25"),
        strategy_pnl=Decimal("10"),
        leverage=Decimal("1.5"),
        available_liquidity=Decimal("50000"),
    )

    assert snapshot.symbol_exposure == Decimal("1100")
    assert snapshot.portfolio_exposure == Decimal("2050")
    assert snapshot.concurrent_trades == 2
    assert snapshot.daily_pnl == Decimal("25")
    assert snapshot.strategy_pnl == Decimal("10")
    assert snapshot.available_liquidity == Decimal("50000")


def test_snapshot_requires_marks_for_open_positions() -> None:
    book = PositionBook()
    book.apply_fill("NSE_EQ|AAA", 1, Decimal("100"))
    with pytest.raises(ValueError, match="missing mark price"):
        book.risk_snapshot({})


def test_flat_positions_do_not_require_marks() -> None:
    book = PositionBook()
    book.apply_fill("NSE_EQ|AAA", 1, Decimal("100"))
    book.apply_fill("NSE_EQ|AAA", -1, Decimal("101"))
    snapshot = book.risk_snapshot({})
    assert snapshot.symbol_exposure == Decimal("0")
    assert snapshot.portfolio_exposure == Decimal("0")
    assert snapshot.concurrent_trades == 0
