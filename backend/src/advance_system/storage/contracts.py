from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, TYPE_CHECKING, runtime_checkable
from urllib.parse import urlparse

if TYPE_CHECKING:
    from advance_system.storage.parquet import ResearchDatasetRef


class StorageMode(StrEnum):
    """Deployment mode for storage connectivity."""

    PAPER = "PAPER"
    LIVE = "LIVE"


@dataclass(frozen=True, slots=True)
class StorageConfig:
    """Connection configuration without embedded credentials or provider SDK state."""

    postgres_dsn: str
    clickhouse_dsn: str
    redis_url: str
    parquet_root: str
    mode: StorageMode = StorageMode.PAPER

    def validate(self) -> None:
        for name, value in (
            ("postgres_dsn", self.postgres_dsn),
            ("clickhouse_dsn", self.clickhouse_dsn),
            ("redis_url", self.redis_url),
            ("parquet_root", self.parquet_root),
        ):
            if not value.strip():
                raise ValueError(f"{name} is required")
        self._validate_scheme(self.postgres_dsn, {"postgresql", "postgres"}, "postgres_dsn")
        self._validate_scheme(self.clickhouse_dsn, {"http", "https", "clickhouse"}, "clickhouse_dsn")
        self._validate_scheme(self.redis_url, {"redis", "rediss"}, "redis_url")
        if self.parquet_root.startswith("http://") or self.parquet_root.startswith("https://"):
            raise ValueError("parquet_root must use a filesystem or object-storage URI, not HTTP")

    @staticmethod
    def _validate_scheme(value: str, allowed: set[str], field_name: str) -> None:
        scheme = urlparse(value).scheme.lower()
        if scheme not in allowed:
            raise ValueError(f"{field_name} has unsupported scheme")

    @classmethod
    def from_environment(cls) -> "StorageConfig":
        """Load storage endpoints from environment; credentials belong in DSN secret stores."""
        import os

        values = {
            "postgres_dsn": os.getenv("ATS_POSTGRES_DSN"),
            "clickhouse_dsn": os.getenv("ATS_CLICKHOUSE_DSN"),
            "redis_url": os.getenv("ATS_REDIS_URL"),
            "parquet_root": os.getenv("ATS_PARQUET_ROOT"),
        }
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise RuntimeError(f"missing required storage environment variables: {', '.join(missing)}")
        mode = StorageMode(os.getenv("ATS_STORAGE_MODE", StorageMode.PAPER))
        config = cls(**values, mode=mode)  # type: ignore[arg-type]
        config.validate()
        return config


class PostgreSQLStore(Protocol):
    """Operational relational persistence boundary."""

    async def execute(self, statement: str, parameters: tuple[object, ...] = ()) -> None:
        ...


class ClickHouseStore(Protocol):
    """High-volume analytical query boundary."""

    async def execute(self, statement: str, parameters: tuple[object, ...] = ()) -> None:
        ...


class RedisStore(Protocol):
    """Hot-state/cache boundary; not the source of truth for orders or positions."""

    async def get(self, key: str) -> bytes | None:
        ...

    async def set(self, key: str, value: bytes, *, ttl_seconds: int | None = None) -> None:
        ...


@runtime_checkable
class ParquetStore(Protocol):
    """Immutable/research dataset boundary for parquet/object storage."""

    async def write_dataset(
        self,
        ref: ResearchDatasetRef,
        payload: bytes,
        *,
        created_at: object | None = None,
    ) -> object:
        ...

    async def read_dataset(self, ref: ResearchDatasetRef) -> bytes:
        ...

    async def read_manifest(self, ref: ResearchDatasetRef) -> object:
        ...
