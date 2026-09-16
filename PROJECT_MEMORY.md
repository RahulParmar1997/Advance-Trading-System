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
- Dedicated `/risk` route consumes the backend `/api/v1/risk` contract server-side with `cache: "no-store"`; backend errors and unavailable data remain explicit and `data` is never synthesized.
- Market State, Scanner and Portfolio routes now likewise consume `/api/v1/market-state`, `/api/v1/scanner` and `/api/v1/portfolio` server-side with `cache: "no-store"` and explicit fail-closed handling.
- Terminal navigation exposes the dedicated Risk route.
- Frontend contract tests cover all four dedicated routes, endpoint consumption, no-store fetch semantics, unavailable handling and execution boundaries.

## Typed terminal API contracts
- `backend/src/advance_system/observability/api.py` defines the stable `TerminalViewResponse` contract and explicit routes for Market State, Scanner, Risk and Portfolio.
- `backend/src/advance_system/observability/server.py` exposes those routes alongside `/metrics`.
- The implementation is deliberately fail-closed: until authoritative providers are connected, each view returns `available=false`, `reason=data_feed_not_connected`, and `data=null`. No market, account, risk or opportunity values are fabricated.
- `backend/src/advance_system/observability/providers.py` provides a provider-owned `TerminalSnapshot` boundary and `TerminalDataService`; provider snapshots are passed through only when the requested view matches exactly.
- POST/PUT/DELETE remain rejected by the observability server; terminal routes have no broker, OMS or RiskEngine authority.
- Deterministic tests cover contract versioning, route completeness, JSON shape, mutation rejection, unavailable providers, exact snapshot passthrough and view mismatch fail-closed behavior.
- An explicit `build_observability_handler` composition boundary accepts a `TerminalSnapshotProvider` dependency. The default server composition supplies no provider, so it remains fail-closed until an authoritative implementation is available.
- Deterministic composition tests verify injected-provider passthrough and no-provider fail-closed behavior.

## Provider discovery
- The repository contains a concrete `UpstoxAdapter` market-data adapter plus Upstox market-status/source components, but no existing application-level `TerminalSnapshotProvider` implementation that safely maps authoritative validated observations into all terminal views.
- The terminal composition layer therefore does not invent or directly couple to partial broker data. A concrete read-only provider remains the next integration task.

## Pending roadmap
1. Verify the current terminal route-consumption commits through GitHub Actions.
2. Introduce/identify the concrete authoritative read-only market-data and account/portfolio provider implementation, then inject it through the terminal composition boundary.
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
Run 594 (`35085263149`) on `cb7a241fce78a2a4e181f97fac5e1ec4b9f61469` was fully successful, including Ruff, unit pytest, Compose validation, frontend checks and Docker Compose runtime smoke. The subsequent terminal route-consumption commits require fresh GitHub Actions verification; no newer green run is being claimed until the final HEAD is verified.

## Next implementation rule
When the user says **NEXT**, inspect current `main` and latest GitHub Actions state, implement the highest-priority unfinished task directly on `main`, add deterministic tests, update this file and `PROJECT_WORK_STATUS.md`, verify CI, and report the commit SHA and blockers.
