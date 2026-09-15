from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class Field(StrEnum):
    REGIME = "regime"
    STRUCTURE_EVENT = "structure_event"
    STRUCTURE_DIRECTION = "structure_direction"
    FVG_DIRECTION = "fvg_direction"
    LIQUIDITY_DISTANCE = "liquidity_distance"
    VOLUME_CONFIRMATION = "volume_confirmation"


class Operator(StrEnum):
    EQ = "eq"
    NE = "ne"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"


@dataclass(frozen=True, slots=True)
class Condition:
    field: Field
    operator: Operator
    value: object

    def evaluate(self, context: Mapping[str, object]) -> bool:
        if self.field.value not in context:
            return False
        left = context[self.field.value]
        right = self.value
        if self.operator is Operator.EQ:
            return left == right
        if self.operator is Operator.NE:
            return left != right
        if self.operator is Operator.LT:
            return left < right
        if self.operator is Operator.LTE:
            return left <= right
        if self.operator is Operator.GT:
            return left > right
        if self.operator is Operator.GTE:
            return left >= right
        raise ValueError(f"unsupported operator: {self.operator}")


@dataclass(frozen=True, slots=True)
class AllOf:
    conditions: tuple[Condition, ...]

    def evaluate(self, context: Mapping[str, object]) -> bool:
        return all(condition.evaluate(context) for condition in self.conditions)


@dataclass(frozen=True, slots=True)
class AnyOf:
    conditions: tuple[Condition, ...]

    def evaluate(self, context: Mapping[str, object]) -> bool:
        return any(condition.evaluate(context) for condition in self.conditions)


@dataclass(frozen=True, slots=True)
class ScannerRule:
    name: str
    expression: AllOf | AnyOf

    def evaluate(self, context: Mapping[str, object]) -> bool:
        if not self.name.strip():
            raise ValueError("scanner rule name is required")
        return self.expression.evaluate(context)


@dataclass(frozen=True, slots=True)
class ScanResult:
    rule: str
    matched: bool
    reasons: tuple[str, ...]


class ScannerEngine:
    """Network/database-independent scanner evaluator."""

    def evaluate(self, rule: ScannerRule, context: Mapping[str, object]) -> ScanResult:
        matched = rule.evaluate(context)
        reasons = tuple(
            f"{condition.field.value} {condition.operator.value} {condition.value}"
            for condition in rule.expression.conditions
            if condition.field.value in context and condition.evaluate(context)
        )
        return ScanResult(rule.name, matched, reasons)
