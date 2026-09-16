# Advance Trading System — Project Memory

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Authoritative branch:** `main` only
**Mode:** PAPER-first; no uncontrolled live execution
**Updated:** 2026-09-16

## Purpose
India-focused Market Intelligence + Quant Research + Automated Trading Platform.

## Architecture invariants
- Market Event → Normalization → Validation → Candle → Features → Market State → Strategy → Opportunity → Probability/EV → RiskEngine → OMS → Paper Fill → Position → P&L → Journal.
- AI/HPC never bypasses RiskEngine or places uncontrolled orders.
- Strategy logic is deterministic, testable, network-independent and database-independent.
- Broker-specific code stays behind adapter boundaries.
- Observed market data and model-derived estimates remain distinguishable.
- Backtests are chronology-safe and free of look-ahead bias.
- PAPER remains the default.
- Work directly on `main`.

## Completed foundation
- Versioned domain contracts; market-data normalization; session-aware candles; data-quality validation; instrument-master versioning.
- Upstox V3 protobuf/transport/source boundaries and authoritative market-status integration.
- Market structure, liquidity, FVG, order-block, regime, breadth, sector, derivatives, option Greeks, futures basis, institutional-flow, Wyckoff and MarketContext primitives.
- Deterministic scanner orchestration/scoring, probability calibration and leakage-safe OOS validation.
- Immutable audit evidence, durable journal and broker reconciliation adapter.
- PostgreSQL/ClickHouse/Redis/Parquet storage boundaries with runtime conformance tests.
- Asyncpg pool lifecycle/concurrency hardening, atomic migration handling and PAPER OMS idempotency collision protection.
- Observational Prometheus metrics, health/readiness checks and Docker Compose runtime smoke validation.

## Frontend terminal
- Dark-first observational Next.js terminal with Market State, Scanner, Risk and PAPER Portfolio panels.
- Responsive styling, UI contract tests, ESLint, TypeScript typecheck and production build in CI.
- Docker standalone image, backend health-gated startup and frontend HTTP healthcheck hardened.
- GitHub Actions Run 549 (`35076782833`) on `874494a6778e445a5b357bbef7821627e6b8fba7` passed Ruff, unit pytest, Compose validation, frontend checks and full Docker Compose runtime smoke.

## Typed terminal API contracts
- `backend/src/advance_system/observability/api.py` defines the stable `TerminalViewResponse` contract and explicit routes for Market State, Scanner, Risk and Portfolio.
- `backend/src/advance_system/observability/server.py` exposes those routes alongside `/metrics`.
- The current implementation is deliberately fail-closed: until authoritative providers are connected, each view returns `available=false`, `reason=data_feed_not_connected`, and `data=null`. No market, account, risk or opportunity values are fabricated.
- `backend/src/advance_system/observability/providers.py` provides a provider-owned `TerminalSnapshot` boundary and `TerminalDataService`; provider snapshots are passed through only when the requested view matches exactly.
- POST/PUT/DELETE remain rejected by the observability server; terminal routes have no broker, OMS or RiskEngine authority.
- Deterministic tests cover contract versioning, route completeness, JSON shape, mutation rejection, unavailable providers, exact snapshot passthrough and view mismatch fail-closed behavior.
- GitHub Actions Runs 557 and 560 identified Ruff import-order defects in the new terminal API/test code; those defects were corrected on `main`.

## Pending roadmap
1. Connect typed terminal endpoints to concrete authoritative market-data/account read-only services at application composition time.
2. Add dedicated market, scanner, risk and portfolio frontend routes while preserving read-only boundaries.
3. Runtime end-to-end monitoring validation outside CI if a persistent deployment environment is required.
4. Additional concrete vendor adapter/factory integration coverage when those drivers are introduced.

## Safety / quality rules
- No fabricated broker fields, market data, probabilities or execution status.
- Validate timestamps, instruments, quantities and session metadata.
- Reject malformed/stale data fail-closed where safety is involved.
- PostgreSQL remains operational source of truth; Redis/ClickHouse/Parquet never become execution authority.
- Research compute is isolated from execution and cannot approve its own trades.
- Do not claim CI green unless GitHub Actions actually confirms it.

## Current verification state
Run 549 (`35076782833`) is the latest fully verified successful baseline. Run 562 (`35078584881`) started against `668c4ea9b38a0ad7913e6ae3ee370f65f155b49d` and was still in progress when this state was recorded; therefore the current HEAD is not yet CI-verified.

## Next implementation rule
When the user says **NEXT**, inspect current `main` and latest GitHub Actions state, implement the highest-priority unfinished task directly on `main`, add deterministic tests, update this file and `PROJECT_WORK_STATUS.md`, verify CI, and report the commit SHA and blockers.
