# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-15

## Latest completed work
- [x] Durable append-only JSONL journal backend with startup integrity validation and checkpoints.
- [x] Next.js/React/TypeScript frontend foundation with dark-first terminal shell and observational landing dashboard.
- [x] Read-only `/market-overview`, `/scanner`, `/derivatives`, `/paper-trading`, `/portfolio`, `/journal`, and `/research` routes with explicit typed contracts.
- [x] Phase 9 storage configuration and PostgreSQL/ClickHouse/Redis/Parquet boundary contracts.
- [x] Concrete PostgreSQL operational adapter with injected connection factory and fail-closed health check.
- [x] Initial PostgreSQL operational migration for orders, fills, and positions.
- [x] Migration version tracking and idempotent PostgreSQL migration runner contract.
- [x] Migration runner unit coverage for pending and already-applied migrations.
- [x] Concrete asyncpg PostgreSQL driver/pool integration with connection lifecycle and transaction context.
- [x] PostgreSQL lifecycle/transaction unit coverage using injected fakes.
- [x] Concrete ClickHouse analytics adapter with injected connection lifecycle and fail-closed health check.
- [x] Initial ClickHouse market-events and feature analytics schema.
- [x] ClickHouse adapter unit coverage.
- [x] Concrete Redis hot-state adapter with TTL, lifecycle, fail-closed health check, and source-of-truth protection.
- [x] Redis adapter unit coverage and hot-state boundary documentation.
- [x] Concrete immutable Parquet/object-storage adapter with content-addressed manifests and explicit dataset versioning.
- [x] Research dataset layout documentation and immutable write/read integrity tests.
- [x] Docker backend/frontend images and local PostgreSQL/ClickHouse/Redis deployment stack.
- [x] PAPER-safe container defaults, non-root runtime, read-only backend filesystem and health-gated dependencies.
- [x] Next.js standalone production output for the frontend image.
- [x] Docker build exclusions for secrets, caches and local dependencies.
- [x] Reverse-proxy configuration with security headers and isolated health endpoint.
- [x] Prometheus monitoring configuration and operational deployment/incident runbook.
- [x] Monitoring remains observational and does not create broker execution authority.
- [x] Ruff quality gate repaired: verified run reports `All checks passed!` for `ruff check src tests`.
- [x] Upstox V3 protobuf decoder boundary restored to the expected generated message surface.
- [x] Backtest partial-fill execution repaired so configured fill caps can produce deterministic split fills without inventing future market data.
- [x] Integrated backtests now accept an explicit authoritative market-status input and continue to fail closed when it is absent.
- [x] PAPER fill tests exercise the canonical OMS path through `CANDIDATE → QUALIFIED → RISK_CHECK → ORDER_PENDING` before fills.
- [x] Storage adapter tests aligned with actual parameter forwarding and fully qualified immutable object keys.
- [x] Market-session, market-context, liquidity, FVG, swing, probability, calibration, regime and volume-profile tests aligned with their current deterministic contracts.
- [x] Upstox feed mapping validates LTP before requiring a fallback message timestamp.
- [x] Changes committed directly to `main`.

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
- [x] Deterministic futures/options metadata and option-chain validation.
- [x] Deterministic Black-Scholes Greeks / implied-volatility analytics.
- [x] Deterministic futures basis analytics.
- [x] Deterministic market breadth and sector breadth analytics.
- [x] Deterministic sector rotation ranking with optional explicit benchmark return.
- [x] Explicit institutional FII/DII flow aggregation; no flow inference from price/volume.
- [x] MarketContextEngine joining completed-candle regime classification with session metadata and fail-closed consistency checks.
- [x] Deterministic Wyckoff features with chronology/look-ahead protections.

### Trading / risk / execution
- [x] Trade Type and versioned Strategy framework.
- [x] Opportunity, probability and EV primitives.
- [x] RiskEngine with hard safety gates and auditable decisions.
- [x] Canonical OMS lifecycle and controlled RiskEngine → PAPER OMS flow.
- [x] PAPER fills, position book, reconciliation, journal and RiskSnapshot integration.
- [x] Upstox reconciliation adapter translating authoritative order/fill responses into broker-neutral contracts.

### Research / audit
- [x] Event-driven backtester with costs, slippage, fees, latency, partial fills and liquidity limits.
- [x] Walk-forward/OOS, Monte Carlo and cost/capacity/regime sensitivity foundations.
- [x] Pattern DNA similarity and leakage-safe ML dataset/calibration primitives.
- [x] Historical probability calibration and strict OOS validation.
- [x] Append-only audit evidence contract with content-addressed immutable records and explicit non-execution authority.
- [x] Durable JSONL journal backend with append-only persistence and startup corruption/duplicate detection.
- [x] Immutable Parquet research dataset persistence with explicit dataset/version/partition addressing.

### Frontend
- [x] Next.js/React/TypeScript application foundation.
- [x] Dark-first terminal shell and navigation.
- [x] Read-only market overview, scanner, derivatives, PAPER trading, portfolio, journal and research dashboards.
- [x] No direct broker/execution action from frontend.
- [x] Standalone Next.js production build configuration.

### Infrastructure
- [x] Explicit storage configuration contract for PostgreSQL, ClickHouse, Redis and Parquet/object storage.
- [x] Storage adapter protocols with vendor-neutral boundaries.
- [x] Environment-only endpoint configuration with no hard-coded credentials.
- [x] Storage source-of-truth and execution-authority rules documented.
- [x] PostgreSQL operational adapter with injected driver lifecycle.
- [x] Initial PostgreSQL schema migration for operational order/fill/position state.
- [x] Migration version tracking and idempotent PostgreSQL migration runner contract.
- [x] Concrete asyncpg driver integration with pooled connection lifecycle.
- [x] Transaction context with commit/rollback semantics delegated to the PostgreSQL driver.
- [x] Concrete ClickHouse analytics adapter with injected connection lifecycle.
- [x] Initial ClickHouse analytics schema for market events and features.
- [x] Concrete Redis hot-state adapter with TTL and lifecycle controls.
- [x] Redis source-of-truth prohibition and hot-state usage documentation.
- [x] Concrete immutable Parquet/object-storage adapter with injected vendor-neutral object boundary.
- [x] Content-addressed dataset manifests and no-overwrite semantics.
- [x] Docker Compose deployment stack for PostgreSQL, ClickHouse, Redis, backend and frontend.
- [x] Backend container runs as non-root with read-only root filesystem.
- [x] Reverse proxy configuration and deployment runbook.
- [x] Prometheus monitoring configuration with application scrape gated until `/metrics` exists.

## Pending work

### Phase 9 — Infrastructure
- [x] Storage configuration and vendor-neutral boundaries.
- [x] PostgreSQL operational adapter boundary.
- [x] Initial PostgreSQL operational migration.
- [x] Migration version tracking contract.
- [x] Concrete PostgreSQL driver integration.
- [x] Concrete ClickHouse analytics adapter/schema.
- [x] Concrete Redis hot-state adapter.
- [x] Concrete Parquet/object-storage adapter and dataset layout.
- [x] Docker/deployment configuration.
- [x] Monitoring, runbooks and reverse proxy.
- [ ] Finish backend test-suite repair and verify CI green.

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

## Current next task
Continue backend test-suite repair and verify the GitHub Actions quality gate. Do not mark CI green until the full suite passes.

## CI note
Latest **verified** run before the current head: commit `883e51e0fab7f6101090634cec0369debfba5ebf` — Ruff passed and pytest reported **288 passed / 11 failed**. Subsequent commits address those remaining failures; the current `main` head has a fresh Actions run in progress and is not yet certified green.
