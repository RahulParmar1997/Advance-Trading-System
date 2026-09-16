# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-16

## Latest completed work
- [x] Observational Prometheus `/metrics` endpoint with deterministic registry/rendering and read-only HTTP semantics.
- [x] Docker Compose monitoring stack with backend/Prometheus health gates and bounded runtime smoke validation.
- [x] PostgreSQL, ClickHouse, Redis and Parquet storage contracts hardened with concrete adapter conformance tests.
- [x] PostgreSQL pooled-connection lifecycle, lazy-pool concurrency, migration cleanup/atomicity, and PAPER OMS idempotency hardened.
- [x] Dark-first observational Next.js terminal with Market State, Scanner, Risk and PAPER Portfolio panels; no broker/execution controls.
- [x] Frontend CI contract tests, lint, typecheck, production build, Docker runtime smoke, standalone-image fix, backend health gate and HTTP healthcheck.
- [x] Verified GitHub Actions Run 549 (`35076782833`) on commit `874494a6778e445a5b357bbef7821627e6b8fba7`: Ruff, unit pytest, Compose validation, frontend install/contract/lint/typecheck/build, and Docker Compose runtime smoke all passed.
- [x] Added versioned read-only terminal API contracts for Market State, Scanner, Risk and Portfolio views. Until authoritative feed-backed providers exist, responses explicitly report `available=false` and `data=null` rather than synthesizing market/account values.
- [x] Exposed the four terminal API routes from the existing backend observability server without adding broker or execution authority.
- [x] Added deterministic HTTP contract tests for versioning, all routes, JSON response shape and rejection of POST.
- [x] Added a provider-owned `TerminalSnapshot` boundary and `TerminalDataService`; terminal HTTP routes now consume that service rather than constructing view payloads themselves.
- [x] Added deterministic provider-service tests covering unavailable state, exact snapshot passthrough, view mismatch fail-closed behavior and all four terminal views.
- [x] Diagnosed the persistent Ruff I001 issue in `observability/api.py` using GitHub Actions feedback and iteratively corrected the import grouping on `main`.

## Pending work
### Frontend / terminal
- [ ] Connect a concrete authoritative market-data/portfolio provider into the terminal service at application composition time.
- [ ] Add dedicated market, scanner, risk and portfolio frontend routes while preserving read-only frontend boundaries.

### Infrastructure / operations
- [ ] Runtime end-to-end monitoring validation outside CI against an actually running deployment environment, if a persistent environment is required.
- [ ] Extend application-level integration coverage to additional concrete vendor adapter/factory implementations when those drivers are introduced.

## Current task
Complete GitHub verification of the terminal API import-layout correction, then continue connecting concrete authoritative market-data and account/read-only providers at application composition time without fabricating data or creating execution authority.

## Latest verified CI state
Runs 568 (`35079804364`), 569 (`35080360349`), 570 (`35080510997`), 571 (`35080647090`) and 572 (`35080710642`) all failed at Ruff I001 in `backend/src/advance_system/observability/api.py`; pytest and later stages were skipped. Their logs were used to apply the successive import-layout corrections. The current `main` HEAD is `44b9ab7c5c8429073b32dd51f1b74051de1d76dd`, with GitHub Actions Run 574 (`35080835719`) queued/pending verification. Run 549 (`35076782833`) remains the latest fully verified successful baseline.

## Architectural decisions
- Mandatory execution path remains `Market Data → Validation → Market Intelligence → Scanner → Trade Type → Strategy → Probability/EV → RiskEngine → OMS → Execution`.
- PostgreSQL is operational source of truth; ClickHouse analytics; Redis ephemeral/hot state; Parquet/object storage immutable research data.
- Frontend and terminal APIs are observational/read-only and cannot invoke broker execution.
- Terminal provider services may expose only authoritative, validated observations; unavailable or mismatched provider data fails closed and is never guessed.
- AI/HPC cannot bypass `RiskEngine → OMS`.

## Main-only requirement
All implementation changes are committed directly to `main`; no feature branches are used unless explicitly requested.
