"""Storage boundary contracts for operational and research persistence."""

from advance_system.storage.clickhouse import ClickHouseAnalyticsStore, ClickHouseStoreAdapter
from advance_system.storage.contracts import (
    ClickHouseStore,
    ParquetStore,
    PostgreSQLStore,
    RedisStore,
    StorageConfig,
    StorageMode,
)
from advance_system.storage.parquet import (
    DatasetManifest,
    ImmutableParquetStore,
    ParquetStoreAdapter,
    ResearchDatasetRef,
)
from advance_system.storage.postgres import PostgresOperationalStore, PostgreSQLStoreAdapter
from advance_system.storage.redis import RedisHotStateStore, RedisStoreAdapter

__all__ = [
    "ClickHouseAnalyticsStore",
    "ClickHouseStore",
    "ClickHouseStoreAdapter",
    "DatasetManifest",
    "ImmutableParquetStore",
    "ParquetStore",
    "ParquetStoreAdapter",
    "PostgresOperationalStore",
    "PostgreSQLStore",
    "PostgreSQLStoreAdapter",
    "RedisHotStateStore",
    "RedisStore",
    "RedisStoreAdapter",
    "ResearchDatasetRef",
    "StorageConfig",
    "StorageMode",
]
