from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from advance_system.scanner.dsl import ScanResult


@dataclass(frozen=True, slots=True)
class Evidence:
    """One deterministic observation supporting a scanner result."""

    field: str
    operator: str
    expected: object
    observed: object
    matched: bool
    source: str = "scanner_context"

    def validate(self) -> None:
        if not self.field.strip():
            raise ValueError("evidence field is required")
        if not self.operator.strip():
            raise ValueError("evidence operator is required")
        if not self.source.strip():
            raise ValueError("evidence source is required")


@dataclass(frozen=True, slots=True)
class ScannerResult:
    """Stable scanner output with explicit evidence and human-readable explanation.

    This contract contains observations and rule matches only. It deliberately
    contains no probability, expected value, risk approval, or broker status.
    """

    rule: str
    matched: bool
    instrument: str | None
    observed_at: datetime | None
    evidence: tuple[Evidence, ...]
    explanation: str

    def validate(self) -> None:
        if not self.rule.strip():
            raise ValueError("scanner result rule is required")
        if self.instrument is not None and not self.instrument.strip():
            raise ValueError("scanner result instrument cannot be blank")
        if self.observed_at is not None and self.observed_at.tzinfo is None:
            raise ValueError("scanner result observed_at must be timezone-aware")
        for item in self.evidence:
            item.validate()
        if not self.explanation.strip():
            raise ValueError("scanner result explanation is required")


def build_scanner_result(result: ScanResult, context: Mapping[str, object]) -> ScannerResult:
    """Convert a DSL result into an auditable result without inventing data."""

    evidence: list[Evidence] = []
    for reason in result.reasons:
        field, operator, expected = reason.split(" ", 2)
        evidence.append(
            Evidence(
                field=field,
                operator=operator,
                expected=expected,
                observed=context.get(field),
                matched=True,
            )
        )

    instrument = context.get("instrument")
    observed_at = context.get("observed_at")
    if instrument is not None and not isinstance(instrument, str):
        raise ValueError("scanner context instrument must be text")
    if observed_at is not None and not isinstance(observed_at, datetime):
        raise ValueError("scanner context observed_at must be datetime")

    if result.matched:
        if evidence:
            explanation = f"Rule '{result.rule}' matched {len(evidence)} explicit condition(s)."
        else:
            explanation = f"Rule '{result.rule}' matched without condition evidence."
    else:
        explanation = f"Rule '{result.rule}' did not match the supplied context."

    output = ScannerResult(
        rule=result.rule,
        matched=result.matched,
        instrument=instrument,
        observed_at=observed_at,
        evidence=tuple(evidence),
        explanation=explanation,
    )
    output.validate()
    return output
