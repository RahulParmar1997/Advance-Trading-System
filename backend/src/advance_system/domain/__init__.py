"""Canonical domain contracts."""

from advance_system.domain.versioning import (
    CURRENT_CONTRACT_VERSIONS,
    ContractName,
    validate_contract_version,
)

__all__ = [
    "CURRENT_CONTRACT_VERSIONS",
    "ContractName",
    "validate_contract_version",
]
