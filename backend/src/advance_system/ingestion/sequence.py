from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SequenceResult:
    accepted: bool
    code: str
    expected: int | None
    received: int


class SequenceGuard:
    """Per-stream monotonic sequence guard. Gaps are observable, not silently repaired."""

    def __init__(self) -> None:
        self._last: dict[str, int] = {}

    def observe(self, stream: str, sequence: int) -> SequenceResult:
        if sequence < 0:
            return SequenceResult(False, "INVALID", self._last.get(stream), sequence)
        previous = self._last.get(stream)
        if previous is None:
            self._last[stream] = sequence
            return SequenceResult(True, "INITIAL", None, sequence)
        if sequence <= previous:
            return SequenceResult(False, "OUT_OF_ORDER", previous + 1, sequence)
        expected = previous + 1
        self._last[stream] = sequence
        if sequence != expected:
            return SequenceResult(True, "GAP", expected, sequence)
        return SequenceResult(True, "VALID", expected, sequence)
