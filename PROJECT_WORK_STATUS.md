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

## Pending work

### Infrastructure / operations
- [ ] Fresh GitHub Actions verification of the corrected integration-test working-directory fix and full Docker Compose runtime smoke, including the explicit storage integration test.
- [ ] Runtime end-to-end monitoring validation outside CI against an actually running deployment environment, if a persistent environment is required. The CI smoke test provides real container execution on GitHub-hosted runners but is not a production deployment validation.
- [ ] Extend application-level integration coverage to the concrete adapter/factory implementations where vendor drivers are introduced; current service integration verifies the deployed database/cache operations themselves.

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
Verify the working-directory correction for the Docker-dependent storage integration test. Run 495 (`35063440412`) on `e55fe46a7bf398edf4dd6df8f4ebc45ceced4637` failed with exactly one runtime-smoke error because the test path was evaluated from repository root. The corrected workflow runs `(cd backend && python -m pytest tests/integration/test_storage_services.py -m integration -q)` after PostgreSQL, ClickHouse and Redis readiness. Do not claim CI green until the fresh Actions run completes successfully. If it passes, proceed to the next persistence/application integration gap. Runtime deployment outside CI remains environment-dependent.

## CI note
Run 487 (`35062475086`) on `adfaba2be8ea07b4c35831910f5f47d6e7bb2958` is verified successful for Ruff, 332 unit tests, Compose configuration validation and Docker Compose runtime smoke. Run 492 (`35062956646`) on `bfd7fe0a6dcb347f5ae9cf8eb5f20b87f03bf7ef` failed at normal pytest with exactly 1 integration-test failure and 332 passing tests because the Docker-dependent test ran before Compose services/environment were provisioned. Run 495 (`35063440412`) on `e55fe46a7bf398edf4dd6df8f4ebc45ceced4637` then verified the isolation itself: Ruff passed, 332 unit tests passed, and Compose configuration passed, but runtime smoke failed because the integration test path was resolved from repository root. The working-directory correction is now committed on `main` as `432dace611bbbc746468dcb107ee7460cd4a2939`; fresh Actions verification is required.
