# Storage Architecture

The platform uses four explicit persistence boundaries. No trading component may treat a cache or research store as the canonical source of order or position state.

| Store | Primary responsibility | Canonical examples |
| --- | --- | --- |
| PostgreSQL | Operational application state | orders, fills, positions, risk decisions, journal indexes |
| ClickHouse | High-volume analytics | normalized market events, features, scan history, analytics |
| Redis | Hot/ephemeral state | freshness, locks, rate-limit state, short-lived cache |
| Parquet/object storage | Immutable research data | raw market data, backtest datasets, research artifacts |

## Configuration

Endpoints are supplied through `ATS_POSTGRES_DSN`, `ATS_CLICKHOUSE_DSN`, `ATS_REDIS_URL`, and `ATS_PARQUET_ROOT`. `ATS_STORAGE_MODE` defaults to `PAPER`.

Credentials must be supplied through the deployment secret-management mechanism referenced by the endpoint configuration. Credentials must not be committed to source, Dockerfiles, examples, or the repository ledger.

## Boundary rules

- PostgreSQL is the operational source of truth for order/position state.
- Redis is never the source of truth for orders or positions.
- ClickHouse is analytical and must not authorize execution.
- Parquet/object storage is immutable/research-oriented and must not authorize execution.
- Strategy calculations remain independent of all storage implementations.
- All production adapters must implement the typed boundary protocols without leaking vendor-specific types into domain code.
