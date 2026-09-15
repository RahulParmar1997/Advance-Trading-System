# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-15

## Latest completed work
- [x] Corrected the remaining GitHub Actions Ruff import-order failure in `test_research_results.py` and pushed the fix directly to `main`.
- [x] Connected immutable COMPUTED research-result provenance to the existing OOS validation and explicit research-approval workflow.
- [x] Added fail-closed OOS→RESEARCH_APPROVED transitions, provenance binding, and timezone-aware approval evidence with no execution authority.
- [x] Added deterministic unit coverage for OOS validation entry, explicit approval, provenance mismatch, duplicate approval and timestamp validation.
- [x] Added cancellation/timeout enforcement around actual research worker execution with cooperative task cancellation and fail-closed wall-clock limits.
- [x] Added deterministic unit coverage for successful worker completion, timeout cancellation, explicit cancellation, and unknown-job cancellation.
- [x] Added concrete immutable ObjectStore-backed research-result persistence using the existing vendor-neutral ObjectStore boundary.
- [x] Added manifest deserialization and fail-closed integrity verification for persisted research results.
- [x] Added deterministic unit coverage for object-store persistence, immutable overwrite rejection, key layout and corrupted-result detection.
- [x] Fixed scheduler Ruff blocker: removed unused `Callable` import from the research scheduler boundary.
- [x] Added immutable research-result provenance contracts covering result SHA-256, size, dataset/strategy/feature/config versions, Git SHA, seed, backend, hardware, environment, resource usage and timezone-aware creation time.
- [x] Added fail-closed validation requiring COMPUTED status, observed metadata, non-negative resource usage and compliance with job resource limits.
- [x] Added deterministic write-once/integrity-checked in-memory research-result persistence coverage; no validation, OOS approval or broker authority is exposed.
- [x] Added a research-only compute job boundary with reproducibility metadata, selectable CPU/GPU backend identity, resource limits and safe local execution semantics.
- [x] Added distributed CPU, distributed GPU and cloud/HPC scheduler adapters behind a vendor-neutral enqueue boundary; adapters never claim worker completion and have no broker authority.
- [x] Durable append-only JSONL journal backend with startup integrity validation and checkpoints.
- [x] Next.js/React/TypeScript frontend foundation with dark-first terminal shell and observational landing dashboard.
- [x] Read-only trading terminal routes and explicit typed contracts.
- [x] PostgreSQL operational source-of-truth boundary, ClickHouse analytics, Redis hot state and immutable Parquet/object storage boundaries.
- [x] Docker/deployment stack, reverse proxy, monitoring configuration and operational runbook.
- [x] Upstox V3 protobuf boundary, market-data validation and deterministic analytics foundations.
- [x] Event-driven backtesting with costs, latency, partial fills and liquidity limits.
- [x] RiskEngine hard gate and canonical OMS → PAPER execution flow.

## Pending work

### Infrastructure / operations
- [ ] Fresh GitHub Actions verification after the latest Ruff correction.
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
Fresh CI verification; after CI is green, implement the production `/metrics` endpoint and end-to-end monitoring validation.

## CI note
Run 439 for commit `dccf31d5e7fd1a3cc0acd428be134107d845d319` failed at Ruff and skipped Pytest. The import-order correction has now been committed as `1db8ed39b7d964418874b3166959699e91992fc4`. Fresh Actions verification is required before certifying CI-green.
