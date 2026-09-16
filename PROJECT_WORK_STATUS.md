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

## Pending work

### Infrastructure / operations
- [ ] GitHub Actions verification of the PAPER OMS idempotency collision fix and full Docker Compose runtime smoke.
- [ ] Runtime end-to-end monitoring validation outside CI against an actually running deployment environment, if a persistent environment is required. The CI smoke test provides real container execution on GitHub-hosted runners but is not a production deployment validation.
- [ ] Extend application-level integration coverage to the concrete adapter/factory implementations where additional vendor drivers are introduced.

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
Verify GitHub Actions for the PAPER OMS idempotency collision fix. Do not claim CI green until the new run completes successfully. If it passes, continue with the next highest-priority persistence/application integration gap.

## CI note
Run 502 (`35064867296`) on `1dbc8ecc2789b4ca6bf6008f0757d63a11f45c25` was the latest verified successful baseline: Ruff passed, unit tests passed, Compose configuration validation passed, and the full Docker Compose runtime/storage integration smoke passed. The current OMS fix is committed on `main` and requires fresh Actions verification.
