# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-15

## Latest completed work
- [x] Fixed scheduler Ruff blocker: removed unused `Callable` import from the research scheduler boundary.
- [x] Added immutable research-result provenance contracts covering result SHA-256, size, dataset/strategy/feature/config versions, Git SHA, seed, backend, hardware, environment, resource usage and timezone-aware creation time.
- [x] Added fail-closed validation requiring COMPUTED status, observed metadata, non-negative resource usage and compliance with job resource limits.
- [x] Added deterministic write-once/integrity-checked in-memory research-result persistence coverage; no validation, OOS approval or broker authority is exposed.
- [x] Added deterministic unit coverage for checksum correctness, metadata requirements, resource limits, overwrite rejection, integrity checks and status non-promotion.
- [x] Added a research-only compute job boundary with reproducibility metadata, selectable CPU/GPU backend identity, resource limits and safe local execution semantics.
- [x] Added distributed CPU, distributed GPU and cloud/HPC scheduler adapters behind a vendor-neutral enqueue boundary; adapters never claim worker completion and have no broker authority.
- [x] Added deterministic unit coverage for research scheduler routing, backend matching and preservation of RAW status until worker execution is actually observed.
- [x] Durable append-only JSONL journal backend with startup integrity validation and checkpoints.
- [x] Next.js/React/TypeScript frontend foundation with dark-first terminal shell and observational landing dashboard.
- [x] Read-only `/market-overview`, `/scanner`, `/derivatives`, `/paper-trading`, `/portfolio`, `/journal`, and `/research` routes with explicit typed contracts.
- [x] Phase 9 storage configuration and PostgreSQL/ClickHouse/Redis/Parquet boundary contracts.
- [x] Concrete PostgreSQL operational adapter with injected connection factory and fail-closed health check.
- [x] Initial PostgreSQL operational migration for orders, fills, and positions.
- [x] Migration version tracking and idempotent PostgreSQL migration runner contract.
- [x] Concrete asyncpg PostgreSQL driver/pool integration with connection lifecycle and transaction context.
- [x] Concrete ClickHouse analytics adapter and initial market-events/features schema.
- [x] Concrete Redis hot-state adapter with TTL, lifecycle, fail-closed health check, and source-of-truth protection.
- [x] Concrete immutable Parquet/object-storage adapter with content-addressed manifests and explicit dataset versioning.
- [x] Docker/deployment stack, reverse proxy, monitoring configuration and operational runbook.
- [x] Upstox V3 protobuf boundary, market-data validation and deterministic analytics foundations.
- [x] Event-driven backtesting with costs, latency, partial fills and liquidity limits.
- [x] RiskEngine hard gate and canonical OMS → PAPER execution flow.

## Done on `main`

### Repository / quality
- [x] Implementation ledger and persistent project memory.
- [x] Backend Python package, pytest/Ruff and GitHub Actions quality workflow.
- [x] Domain contract version registry and explicit contract versions.
- [x] Structured JSON logging with recursive secret redaction.
- [x] Deterministic health/readiness checks.

### Market data / instruments
- [x] Canonical broker-neutral QuoteEvent and normalization boundary.
- [x] Candle engine, ordering protection, volume delta and multi-timeframe/session-aware aggregation.
- [x] Deterministic data-quality service.
- [x] Versioned/content-addressed instrument-master snapshots and monotonic publication.
- [x] Upstox instrument-master adapter and BOD JSON parser boundary.
- [x] Upstox V3 protobuf schema/decoder boundary.
- [x] Real `websockets` transport with injectable connector/decoder.

### Market state / analytics
- [x] India market-session calendar/gate and authoritative market-status contract/source.
- [x] RiskEngine market-status freshness and fail-closed gate.
- [x] Market structure, liquidity, FVG, order-block and regime primitives.
- [x] Unified MarketState foundation.
- [x] Deterministic displacement, candle-volume profile and explicit trade-print order-flow analytics.
- [x] Deterministic derivatives/Greeks/IV/basis/breadth/sector rotation/FII-DII analytics.
- [x] MarketContextEngine and deterministic Wyckoff features with chronology/look-ahead protections.

### Trading / risk / execution
- [x] Trade Type and versioned Strategy framework.
- [x] Opportunity, probability and EV primitives.
- [x] RiskEngine with hard safety gates and auditable decisions.
- [x] Canonical OMS lifecycle and controlled RiskEngine → PAPER OMS flow.
- [x] PAPER fills, position book, reconciliation, journal and RiskSnapshot integration.
- [x] Upstox reconciliation adapter translating authoritative order/fill responses into broker-neutral contracts.

### Research / audit / HPC
- [x] Event-driven backtester with costs, slippage, fees, latency, partial fills and liquidity limits.
- [x] Walk-forward/OOS, Monte Carlo and cost/capacity/regime sensitivity foundations.
- [x] Pattern DNA similarity and leakage-safe ML dataset/calibration primitives.
- [x] Historical probability calibration and strict OOS validation.
- [x] Append-only audit evidence and durable journal persistence.
- [x] Immutable Parquet research dataset persistence.
- [x] Research compute job metadata/resource-control boundary.
- [x] Distributed CPU/GPU and cloud/HPC scheduler adapter boundary with no execution authority.
- [x] Immutable research-result provenance and write-once integrity boundary (test/in-memory persistence implementation).

### Frontend / infrastructure
- [x] Read-only dark-first trading terminal routes and no direct broker execution from frontend.
- [x] PostgreSQL operational source-of-truth boundary and migration/transaction controls.
- [x] ClickHouse analytics, Redis hot state and immutable Parquet storage boundaries.
- [x] Docker Compose deployment stack, non-root/read-only backend container and reverse proxy.
- [x] Prometheus configuration and observational monitoring runbook.

## Pending work

### Research / HPC
- [ ] Add concrete object-storage persistence adapter for research-result manifests/results using the existing immutable ObjectStore boundary.
- [ ] Add cancellation/timeout enforcement around actual worker execution.
- [ ] Connect validated research results to the existing OOS/research-approval workflow without execution authority.

### Infrastructure / operations
- [ ] Production `/metrics` endpoint and end-to-end monitoring validation.
- [ ] Full deployment/integration validation against configured PostgreSQL, ClickHouse and Redis services.

## Non-negotiable architecture rules
- AI never bypasses RiskEngine or places uncontrolled orders.
- Charting is not the source of truth for orders/positions.
- Strategy calculations stay deterministic, testable, network-independent and database-independent.
- Broker-specific code stays behind adapter interfaces.
- Observed market data and model-derived estimates remain explicitly distinguishable.
- Backtests contain no look-ahead bias.
- PAPER remains the default.
- Audit evidence is observational only and must never authorize, submit or mutate an order.
- Journal records are audit/state history only; they are not execution commands.
- Frontend actions must not directly invoke broker execution.
- Redis, ClickHouse and Parquet/object storage must never become execution authority or replace PostgreSQL operational truth.
- Monitoring must remain observational and must not become an execution control plane.
- Research compute must never place orders, mutate positions/balances or bypass RiskEngine → OMS.

## Current next task
Add the concrete immutable ObjectStore-backed research-result persistence adapter, then add worker cancellation/timeout enforcement without introducing execution authority.

## CI note
GitHub Actions run `417` for commit `61505e375f22c59de42610f6ee4f0e9c8b14080f` completed successfully with both Ruff and Pytest. Run `420` for commit `ec43d9dae37c039e7882fff3dd0c642bb5bf3fb9` failed on one Ruff import-order error in the new test; that was corrected on `main`. Run `423` for commit `c0e829a5fe78f5637c9146edfcc1c9cb64e41b2d` is currently in progress; it must complete successfully before CI can be certified green for the result-provenance implementation.
