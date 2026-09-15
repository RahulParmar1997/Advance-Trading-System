# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-15

## Latest completed work
- [x] Durable append-only JSONL journal backend with startup integrity validation and checkpoints.
- [x] Next.js/React/TypeScript frontend foundation with dark-first terminal shell and observational landing dashboard.
- [x] Read-only `/market-overview`, `/scanner` and `/derivatives` dashboard routes with explicit typed contracts.
- [x] Read-only `/paper-trading` terminal with typed order lifecycle/state contract and no order mutation capability.
- [x] Read-only `/portfolio` dashboard with typed position, exposure, P&L and risk-state contracts.
- [x] Read-only `/journal` dashboard with typed audit-event and decision-evidence contracts.
- [x] Journal UI preserves append-only/non-execution semantics and does not reconstruct missing decisions.
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
- [x] Historical probability calibration fit from explicit labeled outcomes, restricted to a chronological training cutoff and out-of-sample application.
- [x] OOS probability validation metrics computed only from samples strictly after the calibration cutoff; fitted models remain immutable.
- [x] Append-only audit evidence contract with content-addressed immutable records and explicit non-execution authority.
- [x] Durable JSONL journal backend with append-only persistence and startup corruption/duplicate detection.

### Frontend
- [x] Next.js/React/TypeScript application foundation.
- [x] App Router root layout, metadata and dark-first global shell.
- [x] Initial market-intelligence terminal landing dashboard.
- [x] Read-only `/market-overview` route with typed market-state contract.
- [x] Terminal navigation shell.
- [x] Read-only `/scanner` dashboard with typed candidate contract.
- [x] Read-only `/derivatives` dashboard with option-chain and futures-basis presentation contracts.
- [x] Read-only `/paper-trading` terminal with typed order state/lifecycle contract.
- [x] Read-only `/portfolio` dashboard with position, exposure, P&L and risk-state contracts.
- [x] Read-only `/journal` dashboard with audit-event and decision-evidence presentation contracts.
- [x] No direct broker/execution action from frontend.

## Pending work

### Phase 8 — Frontend
- [x] Next.js/React/TypeScript foundation.
- [x] Market overview.
- [x] Navigation and scanner dashboard.
- [x] Derivatives dashboard.
- [x] Read-only PAPER trading terminal.
- [x] Portfolio and position dashboard.
- [x] Journal dashboard.
- [ ] Backtest and research UI.

### Phase 9 — Infrastructure
- [ ] PostgreSQL, ClickHouse, Redis and Parquet/object storage.
- [ ] Docker/deployment configuration.
- [ ] Monitoring, runbooks, migrations and reverse proxy.

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

## Current next task
Implement the backtest/research dashboard with read-only run metadata, performance metrics and validation results, without presenting research outputs as execution authority.

## CI note
The latest GitHub Actions state is not verified green. Do not claim the quality gate is healthy until the Ruff failure is repaired and a subsequent run passes both Ruff and pytest.
