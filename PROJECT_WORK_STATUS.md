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
- [x] Added versioned read-only terminal API contracts for Market State, Scanner, Risk and Portfolio views. Until authoritative feed-backed providers exist, responses explicitly report `available=false` and `data=null` rather than synthesizing market/account values.
- [x] Exposed the four terminal API routes from the existing backend observability server without adding broker or execution authority.
- [x] Added deterministic HTTP contract tests for versioning, all routes, JSON response shape and rejection of POST.
- [x] Added a provider-owned `TerminalSnapshot` boundary and `TerminalDataService`; terminal HTTP routes now consume that service rather than constructing view payloads themselves.
- [x] Added deterministic provider-service tests covering unavailable state, exact snapshot passthrough, view mismatch fail-closed behavior and all four terminal views.
- [x] Corrected the persistent Ruff import-layout issue in the terminal API and verified it with GitHub Actions Run 582 (`35082009500`).
- [x] Added an explicit application composition boundary for injecting a `TerminalSnapshotProvider` into the observability handler; the default application composition remains provider-free and therefore fail-closed.
- [x] Added deterministic composition tests proving an injected provider is used and no-provider composition remains unavailable.
- [x] Diagnosed and corrected a Ruff import-order failure in the new composition test (`backend/tests/unit/test_terminal_composition.py`).
- [x] Added the dedicated `/risk` frontend route, wired it to `/api/v1/risk`, added navigation and deterministic frontend contract coverage.
- [x] Replaced static Market State, Scanner and Portfolio frontend placeholders with server-side consumption of `/api/v1/market-state`, `/api/v1/scanner` and `/api/v1/portfolio`, respectively, using `cache: "no-store"` and explicit fail-closed unavailable/error handling.
- [x] Extended frontend contract tests to require backend endpoint consumption and unavailable semantics for all four dedicated terminal routes.

## Pending work
### Frontend / terminal
- [ ] Introduce/identify the concrete authoritative read-only market-data and account/portfolio provider implementation, then inject it through the composition boundary.

### Infrastructure / operations
- [ ] Runtime end-to-end monitoring validation outside CI against an actually running deployment environment, if a persistent environment is required.
- [ ] Extend application-level integration coverage to additional concrete vendor adapter/factory implementations when those drivers are introduced.

## Current task
The dedicated terminal routes now consume their backend contracts. The next integration task is to identify an authoritative read-only market-data and account/portfolio provider and inject it through the existing composition boundary without synthesizing observations.

## Latest verified CI state
Run 594 (`35085263149`) on `cb7a241fce78a2a4e181f97fac5e1ec4b9f61469` was fully successful, including Ruff, unit pytest, Compose validation, frontend checks and Docker Compose runtime smoke. The current route-consumption commits after that run require fresh GitHub Actions verification; no newer green CI run is being claimed until the final HEAD is verified.

## Architectural decisions
- Mandatory execution path remains `Market Data → Validation → Market Intelligence → Scanner → Trade Type → Strategy → Probability/EV → RiskEngine → OMS → Execution`.
- PostgreSQL is operational source of truth; ClickHouse analytics; Redis ephemeral/hot state; Parquet/object storage immutable research data.
- Frontend and terminal APIs are observational/read-only and cannot invoke broker execution.
- Terminal provider services may expose only authoritative, validated observations; unavailable or mismatched provider data fails closed and is never guessed.
- Application composition accepts an explicit `TerminalSnapshotProvider`; no provider is created implicitly, preserving fail-closed behavior until an authoritative implementation exists.
- Frontend server routes may consume backend terminal contracts, but they must preserve `available`, `reason`, and `data=null` semantics on unavailable/error responses.
- AI/HPC cannot bypass `RiskEngine → OMS`.

## Main-only requirement
All implementation changes are committed directly to `main`; no feature branches are used unless explicitly requested.
