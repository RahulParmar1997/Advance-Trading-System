# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-15

## Current status
The repository has a substantial deterministic PAPER/research foundation. Upstox transport/protobuf boundaries remain isolated behind adapters. Instrument-master ingestion has a concrete Upstox BOD JSON source, authoritative exchange status is enforced by the RiskEngine, and the official Upstox V3 protobuf schema is vendored/pinned behind the decoder boundary. Multi-timeframe candles are session-aware when configured with the India market-session calendar. Feature analytics include deterministic displacement, candle-volume profile and an explicit trade-print order-flow boundary. Futures/options analytics now has deterministic contract metadata and option-chain validation based only on authoritative fields supplied by the instrument source.

## Latest completed work
- [x] Added deterministic `DerivativeContract`, `DerivativeType` and `OptionType` contracts.
- [x] Added safe parsing for underlying, expiry, strike, lot size and tick size.
- [x] Added validation separating futures from options and requiring option strike/type metadata.
- [x] Added deterministic `OptionChain` construction keyed by underlying and expiry.
- [x] Added duplicate, mismatch and malformed-metadata protections.
- [x] Added unit coverage for futures/options parsing and option-chain validation.
- [x] Added `PROJECT_MEMORY.md` as the persistent project memory/handoff store.
- [x] Changes committed directly to `main`.

## Done on `main`

### Repository / quality
- [x] `PROJECT_WORK_STATUS.md` implementation ledger.
- [x] `PROJECT_MEMORY.md` persistent project memory and handoff.
- [x] Backend Python package, pytest and Ruff configuration.
- [x] CI workflow for pushes to `main` and pull requests.
- [x] Domain contract version registry and explicit contract versions.
- [x] Structured JSON logging with recursive secret redaction.
- [x] Deterministic health/readiness checks.

### Market data / instruments
- [x] Canonical broker-neutral `QuoteEvent` and normalization boundary.
- [x] Candle engine, ordering protection, volume delta and feature foundation.
- [x] Multi-timeframe candle aggregation with independent interval state.
- [x] Session-aware candle boundaries and session metadata.
- [x] Deterministic data-quality service.
- [x] Broker-neutral `MarketDataAdapter` protocol.
- [x] Versioned, sorted, content-addressed instrument-master snapshots.
- [x] Monotonic atomic instrument-master publication.
- [x] Upstox instrument-master adapter boundary.
- [x] Concrete Upstox BOD JSON instrument-master source and parser.
- [x] Upstox V3 protobuf schema/artifact vendoring and pinning.
- [x] Upstox V3 protobuf decoder boundary and deterministic feed mapper.
- [x] Real `websockets` transport with injectable connector/decoder.

### Market state / analytics
- [x] India market-session calendar/gate foundation.
- [x] Broker-neutral authoritative market-status contract.
- [x] Upstox exchange market-status source.
- [x] RiskEngine market-status freshness and fail-closed gate.
- [x] Market structure, liquidity, FVG, order-block and regime primitives.
- [x] Unified `MarketState` foundation.
- [x] Deterministic displacement feature engine.
- [x] Deterministic candle-volume profile.
- [x] Explicit trade-print order-flow boundary.
- [x] Deterministic futures/options contract metadata and option-chain validation.

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

### Phase 3 — Market state / analytics
- [x] Multi-timeframe candle aggregation foundation.
- [x] Session-aware candle boundaries and session metadata.
- [x] Expanded feature engine and displacement confirmation.
- [x] Candle-volume profile analytics.
- [x] Explicit order-flow analytics boundary.
- [x] Futures/options contract metadata and option-chain foundation.
- [ ] Option Greeks/IV analytics only when authoritative quote/contract inputs support calculation.
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
Implement option Greeks / implied-volatility analytics only where authoritative option quotes, strike, expiry and underlying inputs are available. Keep calculations deterministic, explicit about assumptions, and fail closed on missing/invalid inputs. Keep all work directly on `main`.
