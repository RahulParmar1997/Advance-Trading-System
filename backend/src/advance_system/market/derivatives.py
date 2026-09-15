from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Iterable


class OptionType(StrEnum):
    CALL = "CE"
    PUT = "PE"


class DerivativeType(StrEnum):
    FUTURE = "FUTURE"
    OPTION = "OPTION"


@dataclass(frozen=True, slots=True)
class DerivativeContract:
    instrument: str
    exchange: str
    symbol: str
    derivative_type: DerivativeType
    underlying: str
    expiry: date
    strike: Decimal | None = None
    option_type: OptionType | None = None
    lot_size: int | None = None
    tick_size: Decimal | None = None

    def validate(self) -> None:
        if not self.instrument.strip() or not self.exchange.strip() or not self.symbol.strip():
            raise ValueError("instrument, exchange and symbol are required")
        if not self.underlying.strip():
            raise ValueError("underlying is required")
        if self.expiry is None:
            raise ValueError("expiry is required")
        if self.derivative_type == DerivativeType.OPTION:
            if self.strike is None or self.strike <= 0:
                raise ValueError("option strike must be positive")
            if self.option_type is None:
                raise ValueError("option type is required for options")
        elif self.strike is not None or self.option_type is not None:
            raise ValueError("futures cannot have option strike/type")
        if self.lot_size is not None and self.lot_size <= 0:
            raise ValueError("lot size must be positive")
        if self.tick_size is not None and self.tick_size <= 0:
            raise ValueError("tick size must be positive")


@dataclass(frozen=True, slots=True)
class OptionChain:
    underlying: str
    expiry: date
    contracts: tuple[DerivativeContract, ...]

    @classmethod
    def build(cls, contracts: Iterable[DerivativeContract], *, underlying: str, expiry: date) -> "OptionChain":
        if not underlying.strip():
            raise ValueError("underlying is required")
        selected = tuple(contracts)
        if not selected:
            raise ValueError("option chain cannot be empty")
        for contract in selected:
            contract.validate()
            if contract.derivative_type != DerivativeType.OPTION:
                raise ValueError("option chain contains non-option contract")
            if contract.underlying != underlying or contract.expiry != expiry:
                raise ValueError("option chain contract does not match chain key")
        ordered = tuple(sorted(selected, key=lambda c: (c.strike or Decimal("0"), c.option_type or OptionType.CALL, c.instrument)))
        if len({c.instrument for c in ordered}) != len(ordered):
            raise ValueError("duplicate option instrument")
        return cls(underlying=underlying, expiry=expiry, contracts=ordered)


def parse_derivative_record(record: dict[str, object]) -> DerivativeContract:
    """Map authoritative instrument-master fields without guessing missing metadata."""
    required = ("instrument_key", "exchange", "trading_symbol", "instrument_type")
    missing = [name for name in required if not isinstance(record.get(name), str) or not record[name].strip()]
    if missing:
        raise ValueError(f"missing required derivative fields: {', '.join(missing)}")

    instrument_type = str(record["instrument_type"]).strip().upper()
    if instrument_type not in {"FUT", "CE", "PE"}:
        raise ValueError("record is not a supported derivative")

    underlying = record.get("underlying_symbol") or record.get("underlying_key")
    expiry_raw = record.get("expiry")
    if not isinstance(underlying, str) or not underlying.strip():
        raise ValueError("derivative underlying is required")
    if not isinstance(expiry_raw, str) or not expiry_raw.strip():
        raise ValueError("derivative expiry is required")
    try:
        expiry = date.fromisoformat(expiry_raw.strip()[:10])
    except ValueError as exc:
        raise ValueError("derivative expiry must be ISO date") from exc

    strike_raw = record.get("strike_price")
    strike = None if strike_raw in (None, "") else Decimal(str(strike_raw))
    option_type = OptionType(instrument_type) if instrument_type in {"CE", "PE"} else None
    lot_raw = record.get("lot_size")
    lot_size = None if lot_raw in (None, "") else int(lot_raw)
    tick_raw = record.get("tick_size")
    tick_size = None if tick_raw in (None, "") else Decimal(str(tick_raw))

    contract = DerivativeContract(
        instrument=str(record["instrument_key"]).strip(),
        exchange=str(record["exchange"]).strip().upper(),
        symbol=str(record["trading_symbol"]).strip(),
        derivative_type=DerivativeType.FUTURE if instrument_type == "FUT" else DerivativeType.OPTION,
        underlying=underlying.strip(),
        expiry=expiry,
        strike=strike,
        option_type=option_type,
        lot_size=lot_size,
        tick_size=tick_size,
    )
    contract.validate()
    return contract
