import pytest

from advance_system.trading.trade_types import TradeType, TradeTypeDefinition, TradeTypeRegistry


def test_registry_qualifies_only_enabled_types_with_required_context():
    registry = TradeTypeRegistry(
        (
            TradeTypeDefinition(TradeType.BREAKOUT, required_context=("regime", "structure_event")),
            TradeTypeDefinition(TradeType.RANGE, enabled=False),
            TradeTypeDefinition(TradeType.REVERSAL, required_context=("liquidity_sweep",)),
        )
    )
    assert registry.qualify({"regime": "TREND_UP", "structure_event": "BOS"}) == (TradeType.BREAKOUT,)


def test_duplicate_registration_is_rejected():
    registry = TradeTypeRegistry((TradeTypeDefinition(TradeType.BREAKOUT),))
    with pytest.raises(ValueError):
        registry.register(TradeTypeDefinition(TradeType.BREAKOUT))


def test_disabled_definition_never_qualifies():
    definition = TradeTypeDefinition(TradeType.RANGE, enabled=False)
    assert not definition.qualifies({})
