# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-14

## Current status
The repository has a substantial deterministic PAPER/research foundation. Upstox transport/protobuf boundaries remain isolated behind adapters. Instrument-master ingestion now has a concrete Upstox BOD JSON source with strict parsing and broker-neutral mapping.

## Latest completed work
- [x] Upstox BOD instrument-master JSON source implemented with an injected HTTP boundary.
- [x] Upstox instrument records mapped to the broker-neutral instrument-master contract.
- [x] Parser fails closed on empty, malformed, non-array and incomplete payloads.
- [x] Unit coverage added for equity, index, future and option mappings.
- [x] Changes committed directly to `main`.

## Done on `main`

### Repository / quality
- [x] `PROJECT_WORK_STATUS.md` implementation ledger.
- [x] Backend Python package, pytest and Ruff configuration.
- [x] CI workflow for pushes to `main` and pull requests.
- [x] Domain contract version registry and explicit contract versions.
- [x] Structured JSON logging with recursive secret redaction.
- [x] Deterministic health/readiness checks.

### Market data / instruments
- [x] Canonical broker-neutral `QuoteEvent` and normalization boundary.
- [x] Candle engine, ordering protection, volume delta and feature foundation.
- [x] Deterministic data-quality service.
- [x] Broker-neutral `MarketDataAdapter` protocol.
- [x] Versioned, sorted, content-addressed instrument-master snapshots.
- [x] Monotonic atomic instrument-master publication.
- [x] Upstox instrument-master adapter boundary.
- [x] Concrete Upstox BOD JSON instrument-master source and parser.
- [x] Upstox V3 protobuf decoder boundary and deterministic feed mapper.
- [x] Real `websockets` transport with injectable connector/decoder.

### Market state / analytics
- [x] India market-session calendar/gate foundation.
- [x] Market structure, liquidity, FVG, order-block and regime primitives.
- [x] Unified `MarketState` foundation.

### Trading / risk / execution
- [x] Trade Type and versioned Strategy framework.
- [x] Opportunity, probability and EV primitives.
- [x] RiskEngine with hard safety gates and auditable decisions.
- [x] Canonical OMS lifecycle and controlled RiskEngine → PAPER OMS flow.
- [x] PAPER fills, position book, reconciliation, journal and RiskSnapshot integration.

### Research
- [x] Event-driven backtester with chronology, slippage, fees, latency, partial fills and liquidity limits.
- [x] Walk-forward/OOS, Monte Carlo and cost/capacity/regime sensitivity foundations.
- [x] Pattern DNA similarity and leakage-safe ML dataset/calibration primitives.

## Pending work

### Phase 2 — Market data
- [x] Production-safe secret-backed token store.
- [x] Real WebSocket transport.
- [x] Upstox V3 protobuf decoder boundary.
- [x] Instrument-master ingestion/update foundation.
- [x] Concrete Upstox BOD JSON instrument-master source.
- [x] Production Upstox exchange market-status source.
- [ ] Wire authoritative Upstox status into the RiskEngine market-open gate.
- [ ] Add market-status freshness/staleness protection and fail-closed behavior.
- [ ] Vendor/pin actual generated Upstox V3 protobuf module artifact.

### Phase 3 — Market state / analytics
- [ ] Multi-timeframe candle/session engine.
- [ ] Expanded feature engine and displacement confirmation.
- [ ] Volume profile/order flow where feed data supports it.
- [ ] Futures/options analytics.
- [ ] Breadth, sector rotation and institutional-flow intelligence.
- [ ] Richer regime/session context integration.

### Phase 4 — Intelligence / scanning
- [ ] Wyckoff features.
- [ ] Richer scanner result contracts and explanations.
- [ ] Multi-symbol / multi-timeframe scanner orchestration.

### Phase 5 — Trading decision engine
- [ ] Evidence-based scoring.
- [ ] Historical probability calibration.
- [ ] OOS probability validation.
- [ ] Explanation/audit evidence persistence.

### Phase 6 — Risk / execution
- [ ] Broker reconciliation adapter implementation.
- [ ] Stronger durable journal backend.

### Phase 8 — Frontend
- [ ] Next.js/React/TypeScript foundation.
- [ ] Trading terminal and market dashboard.
- [ ] Scanner, derivatives and PAPER trading views.
- [ ] Portfolio, journal, backtest and research UI.

### Phase 9 — Infrastructure
- [ ] PostgreSQL, ClickHouse, Redis and Parquet/object storage.
- [ ] Docker/deployment configuration.
- [ ] Monitoring and operational runbooks.
- [ ] Migrations and reverse proxy.

## Non-negotiable architecture rules
- AI never bypasses RiskEngine.
- AI never places uncontrolled orders.
- Charting is not the source of truth for orders/positions.
- Strategy calculations stay deterministic, testable, network-independent and database-independent.
- Broker-specific code stays behind adapter interfaces.
- Observed data and model-derived estimates remain explicitly distinguishable.
- Backtests contain no look-ahead bias.
- PAPER remains the default.

## First production milestone
`Market Event → Normalization → Validation → Candle → Features → Market State → Strategy → Opportunity → Probability/EV → RiskEngine → OMS → Paper Fill → Position → P&L → Journal`

## Current next task
Wire the authoritative Upstox exchange-status source into the existing market-session/RiskEngine gate, with freshness limits and fail-closed semantics. Keep all work directly on `main`.
