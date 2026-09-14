from __future__ import annotations

from enum import StrEnum


class ContractName(StrEnum):
    """Stable identifiers for serialized/domain contract families."""

    QUOTE_EVENT = "quote_event"
    OPPORTUNITY = "opportunity"
    ORDER = "order"
    BACKTEST_EVENT = "backtest_event"


CURRENT_CONTRACT_VERSIONS: dict[ContractName, int] = {
    ContractName.QUOTE_EVENT: 1,
    ContractName.OPPORTUNITY: 1,
    ContractName.ORDER: 1,
    ContractName.BACKTEST_EVENT: 1,
}


def validate_contract_version(contract: ContractName, version: int) -> None:
    """Reject unknown contract versions before they enter the domain.

    Version 1 is the initial compatible schema. New schema versions must be
    added explicitly to ``CURRENT_CONTRACT_VERSIONS`` rather than silently
    accepting arbitrary integers.
    """

    if version != CURRENT_CONTRACT_VERSIONS[contract]:
        raise ValueError(
            f"unsupported {contract.value} contract_version: {version}; "
            f"supported version is {CURRENT_CONTRACT_VERSIONS[contract]}"
        )
