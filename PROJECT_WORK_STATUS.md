# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-16

## Latest completed work
- [x] Implemented an observational Prometheus `/metrics` registry and read-only HTTP endpoint using only the Python standard library.
- [x] Added deterministic metric rendering, label escaping/validation, counter/gauge semantics and read-only HTTP method enforcement.
- [x] Wired the backend container to serve metrics on port 8000 and published that port in Docker Compose; the endpoint has no broker, OMS or RiskEngine authority.
- [x] Fixed the `/metrics` renderer to safely handle integer metric samples as well as floating-point samples.
- [x] Added unit coverage for rendering, escaping, validation, HTTP response/content type and read-only behavior.
- [x] Wired a pinned Prometheus service into Docker Compose with the repository deployment configuration mounted read-only, persistent Prometheus storage, and configurable host port 9090.
- [x] Added deterministic deployment-wiring tests confirming the Prometheus service, read-only configuration mount, exposed port, and backend `/metrics` scrape target.
- [x] Added backend and Prometheus Docker healthchecks and deterministic coverage for health-gated monitoring startup.
- [x] Hardened `HealthChecker.check()` so an empty check set fails closed.
- [x] Added a CI guard that runs `docker compose config --quiet` with a CI-only PostgreSQL password.
- [x] Added a GitHub Actions Docker Compose runtime smoke test covering backend metrics, Prometheus readiness, PostgreSQL readiness, ClickHouse ping, Redis ping, and Prometheus backend target health/scrape URL.
- [x] Corrected the runtime smoke Prometheus target label to the configured `advance-trading-system` job.
- [x] Hardened Prometheus readiness polling and PostgreSQL/ClickHouse/Redis readiness polling with bounded retries and fail-closed diagnostics.
- [x] Fixed the ClickHouse smoke probe to avoid `wget | grep -q` SIGPIPE false negatives under `pipefail`.
- [x] Hardened Prometheus target verification with an initial scrape window and a non-zero `lastScrape` requirement.
- [x] Verified GitHub Actions Run 487 (`35062475086`) on commit `adfaba2be8ea07b4c35831910f5f47d6e7bb2958`: Ruff passed, Pytest passed (332 tests), Compose configuration validation passed, and the full Docker Compose runtime smoke test passed.
- [x] Added `backend/tests/integration/test_storage_services.py` covering real PostgreSQL temporary-table write/read, ClickHouse query execution, and Redis set/get/delete operations against the Compose services.
- [x] Isolated Docker-dependent integration tests from the normal unit pytest invocation with an explicit `integration` marker and CI `-m "not integration"` unit-suite selection.
- [x] Diagnosed Run 495 (`35063440412`) failure: unit validation passed (332 tests), but the runtime smoke invoked the integration test from repository root, so pytest could not resolve `tests/integration/test_storage_services.py`.
- [x] Corrected the runtime smoke to execute the storage integration test from `backend` while retaining Docker Compose execution from repository root.
- [x] Diagnosed Run 497 (`35063728912`) storage integration assertion failure: PostgreSQL `psql -tAc` emitted command-status lines (`CREATE TABLE`, `INSERT 0 1`) in addition to the selected value.
- [x] Hardened the PostgreSQL integration assertion to use quiet, tuples-only, unaligned output (`-qAt`) so the test validates the returned value deterministically.
- [x] Fixed the concrete `AsyncpgConnectionFactory` lifecycle so acquired pooled connections are returned with `pool.release()` when the store closes them, rather than calling the raw asyncpg connection's `close()`.
- [x] Added unit coverage proving pooled connections delegate operations, return exactly once to the pool, and remain open at the driver-connection level until pool shutdown.
- [x] Fixed PAPER OMS idempotency so reusing an existing client key with a different order ID fails closed instead of silently replaying the original order.
- [x] Added unit coverage for the client-key/different-order collision case.
- [x] Verified GitHub Actions Run 506 (`35065625581`) on commit `c6cd5df92e5b3afd89d5837956634aeb9c2a9e86`: Ruff passed, 334 unit tests passed with 1 integration test deselected, Compose configuration validation passed, the real PostgreSQL/ClickHouse/Redis storage integration test passed, and the full Docker Compose runtime smoke test passed.
- [x] Serialized `AsyncpgConnectionFactory` lazy pool initialization with an async lock so concurrent first callers share one initialized pool instead of racing to create multiple PostgreSQL pools.
- [x] Added a deterministic concurrency test proving two simultaneous first calls share one initialized pool.
- [x] Verified GitHub Actions Run 510 (`35066042755`) on commit `ff2995aca8121e301e3732a8de2fa6736aa27735`: Ruff, unit pytest, Docker Compose configuration validation, and full Docker Compose runtime smoke all passed.
- [x] Hardened `MigrationRunner` connection lifecycle so every acquired migration connection is closed/released in a `finally` block, including migration failure paths.
- [x] Extended migration unit coverage to verify connection cleanup on successful, idempotent, and failed runs.
- [x] Verified GitHub Actions Run 514 (`35066789576`) on commit `55061e174e39650677488401d402c576c7add60c`: Ruff, unit pytest, Docker Compose configuration validation, and full Docker Compose runtime smoke all passed.
- [x] Hardened `MigrationRunner` transaction atomicity so migration SQL and `schema_migrations` bookkeeping run within one PostgreSQL transaction and rollback on failure.
- [x] Added deterministic migration tests for transaction start/commit, rollback of partial migration application, idempotency, and connection cleanup.
- [x] Verified GitHub Actions Run 519 (`35067255577`) on commit `4522dc22ad55b1a65fbee262b1332d322ef5b45f`: Ruff, unit pytest, Docker Compose configuration validation, and full Docker Compose runtime smoke all passed.
- [x] Aligned the `ParquetStore` application contract with the concrete immutable adapter's versioned `ResearchDatasetRef` API, manifest return type, and dataset read/write methods.
- [x] Added deterministic unit coverage proving the concrete Parquet adapter conforms to the application storage protocol alongside the existing concrete PostgreSQL, ClickHouse and Redis adapter coverage.
- [x] Extended PostgreSQL, ClickHouse and Redis storage protocols with runtime-checkable contracts and added deterministic conformance assertions for all four concrete storage adapters.
- [x] Verified GitHub Actions Run 527 (`35068304434`) on commit `b77b3f11f2e3b3ff78156ec165dcf152ebdecd30`: Ruff, unit pytest, Docker Compose configuration validation, and full Docker Compose runtime smoke all passed.
- [x] Reworked the Next.js frontend into a dark-first observational trading-terminal overview with explicit Market State, Scanner, Risk and PAPER Portfolio panels, navigation, feed-state messaging and an explicit RiskEngine → OMS execution boundary.
- [x] Added responsive terminal styling for desktop, tablet and mobile layouts without introducing broker/execution controls.
- [x] Added deterministic Node-based frontend UI contract tests covering required panels, PAPER mode, disconnected-feed state and execution-boundary messaging.
- [x] Added frontend ESLint configuration, lint/typecheck/test scripts, and GitHub Actions verification for frontend install, contract tests, lint, typecheck and production build.
- [x] Extended the Docker Compose runtime smoke test to build/start the frontend container and verify its served HTML contains the observational terminal title, PAPER mode indicator and RiskEngine → OMS safety boundary.

## Pending work

### Infrastructure / operations
- [ ] Runtime end-to-end monitoring validation outside CI against an actually running deployment environment, if a persistent environment is required. The CI smoke test provides real container execution on GitHub-hosted runners but is not a production deployment validation.
- [ ] Extend application-level integration coverage to additional concrete vendor adapter/factory implementations when those drivers are introduced.

### Frontend / terminal
- [ ] Connect terminal panels to typed backend read-only endpoints once those endpoints/contracts are introduced.
- [ ] Add dedicated market, scanner, risk and portfolio routes while preserving read-only frontend boundaries.

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
Connect the observational terminal to typed, read-only backend endpoints/contracts when those endpoints are introduced; otherwise continue with the next concrete frontend route or backend contract gap without adding execution authority to the UI.

## CI note
The frontend runtime smoke enhancement is committed on `main` as `5c0835d2aaf8cc0ecc92b4f8952863ff8cb6b8f8` and requires its new GitHub Actions run to complete successfully before this change is considered verified.
