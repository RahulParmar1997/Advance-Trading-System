# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-15

## Latest completed work
- [x] Deterministic Wyckoff event features from completed candles and explicit volume inputs.
- [x] Rich scanner result contract with explicit evidence, context identity and deterministic explanations.
- [x] Multi-symbol / multi-timeframe scanner orchestration with explicit scope identity and deterministic ordering.
- [x] Evidence-based scanner scoring using explicit evidence and deterministic non-probabilistic weights.
- [x] Unit coverage for scanner evidence, explanations, orchestration and scoring.
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

### Research
- [x] Event-driven backtester with costs, slippage, fees, latency, partial fills and liquidity limits.
- [x] Walk-forward/OOS, Monte Carlo and cost/capacity/regime sensitivity foundations.
- [x] Pattern DNA similarity and leakage-safe ML dataset/calibration primitives.

## Pending work

### Phase 5 — Trading decision engine
- [x] Evidence-based scoring.
- [ ] Historical probability calibration.
- [ ] OOS probability validation.
- [ ] Explanation/audit evidence persistence.

### Phase 6 — Risk / execution
- [ ] Broker reconciliation adapter implementation.
- [ ] Stronger durable journal backend.

### Phase 8 — Frontend
- [ ] Next.js/React/TypeScript foundation.
- [ ] Trading terminal, dashboards, scanner, derivatives, PAPER trading, portfolio, journal, backtest and research UI.

### Phase 9 — Infrastructure
- [ ] PostgreSQL, ClickHouse, Redis and Parquet/object storage.
- [ ] Docker/deployment configuration.
- [ ] Monitoring, runbooks, migrations and reverse proxy.

## Non-negotiable architecture rules
- AI never bypasses RiskEngine or places uncontrolled orders.
- Charting is not the source of truth for orders/positions.
- Strategy calculations stay deterministic, testable, network-independent and database-independent.
- Broker-specific code stays behind adapter interfaces.
- Observed data and model-derived estimates remain explicitly distinguishable.
- Backtests contain no look-ahead bias.
- PAPER remains the default.

## Current next task
Implement historical probability calibration from labeled historical outcomes, keeping calibration data separate from in-sample scanner scoring and preventing look-ahead/leakage. Keep all work directly on `main`.

## CI note
The latest known GitHub Actions state is not verified green. Do not claim the quality gate is healthy until the Ruff failure is repaired and a subsequent run passes both Ruff and pytest.
