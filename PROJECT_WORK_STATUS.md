# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-14

## Working rule
All normal implementation is committed directly to `main`. Before changes: inspect current state, preserve `RiskEngine → OMS`, keep PAPER default, add/update tests, and update this file. Do not use feature branches unless the project owner explicitly changes the rule.

## Product goal
Build the India-focused Market Intelligence + Quant Research + Automated Trading Platform defined by the project specifications.

Core flow:
`DATA → MARKET STATE → INTELLIGENCE → REGIME → SCANNER → TRADE TYPE → STRATEGY → OPPORTUNITY → PROBABILITY → EV → RISK → OMS → EXECUTION → POSITION → JOURNAL → PATTERN DNA → RESEARCH/ML`

## Done on `main`

### Repository foundation
- [x] `PROJECT_WORK_STATUS.md` established as the implementation ledger.
- [x] Backend Python package foundation established.
- [x] Backend `pyproject.toml` and pytest configuration established.
- [x] Backend test CI workflow added for pushes to `main` and pull requests.
- [x] Domain / ingestion / market package boundaries established.

### Market-data foundation
- [x] Canonical broker-neutral `QuoteEvent` contract.
- [x] Validation for instrument, timezone-aware timestamp, price, bid/ask and volume.
- [x] Broker-shaped `RawQuote` normalization boundary.
- [x] Deterministic fixed-interval candle engine.
- [x] Per-instrument ordering protection.
- [x] Cumulative-volume-to-candle-delta handling.
- [x] Deterministic basic candle feature engine.
- [x] Unit tests for normalization, validation, candle boundary behavior, volume delta, ordering and features.
- [x] Deterministic `DataQualityService` for stale, future, duplicate, out-of-order and timestamp-gap observations.
- [x] Broker-neutral `MarketDataAdapter` protocol and normalization pipeline.
- [x] Unit tests for data-quality rules and broker-neutral ingestion boundary.

## Previously prototyped — not used as the implementation branch
A temporary `foundation/paper-vertical-slice` prototype existed before the main-only rule. Its useful ideas were reviewed and recreated deliberately on `main`; it is not the active development branch.

## Pending work

### Phase 1 — Engineering foundation
- [ ] Configuration/environment handling.
- [ ] Domain contract versioning.
- [ ] Structured logging.
- [ ] Health/readiness checks.
- [ ] Broader CI quality gates.

### Phase 2 — Market data
- [ ] Upstox adapter implementation.
- [ ] Authentication/token lifecycle.
- [ ] WebSocket ingestion.
- [ ] Reconnect/heartbeat handling.
- [ ] Sequence-aware feed validation.
- [ ] Instrument master.

### Phase 3 — Market state / analytics
- [ ] Multi-timeframe candle/session engine.
- [ ] Expanded feature engine.
- [ ] Market structure: swings, HH/HL/LH/LL, BOS, CHoCH, MSS, displacement.
- [ ] Liquidity, FVG, order blocks and supply/demand.
- [ ] Volume profile/order flow where feed data supports it.
- [ ] Futures/options analytics.
- [ ] Breadth, sector rotation and institutional-flow intelligence.
- [ ] Market-regime engine.

### Phase 4 — Intelligence / scanning
- [ ] Typed scanner DSL / AST.
- [ ] Cheap-to-expensive scanner pipeline.
- [ ] Wyckoff features.
- [ ] Scanner result contracts and explanations.

### Phase 5 — Trading decision engine
- [ ] Trade Type framework.
- [ ] Versioned deterministic Strategy interface.
- [ ] Strategy registry.
- [ ] Opportunity engine.
- [ ] Evidence-based scoring.
- [ ] Probability and calibration layer.
- [ ] Expected-value calculation.
- [ ] Explanation/audit evidence.

### Phase 6 — Risk / execution
- [ ] Full RiskEngine limits and position sizing.
- [ ] Exposure, leverage, liquidity and slippage controls.
- [ ] Kill switch and circuit breakers.
- [ ] Canonical OMS state machine.
- [ ] Idempotency and reconciliation.
- [ ] Paper execution.
- [ ] Position manager, P&L and audit trail.

### Phase 7 — Research
- [ ] Event-driven backtester.
- [ ] Realistic costs/fills/slippage/latency/partial fills/rejections.
- [ ] Walk-forward/OOS validation.
- [ ] Monte Carlo and regime/cost/capacity sensitivity.
- [ ] Pattern DNA and similarity search.
- [ ] ML datasets and calibration.

### Phase 8 — Frontend
- [ ] Next.js/React/TypeScript foundation.
- [ ] Trading terminal, market dashboard and charts.
- [ ] Scanner, futures/options and PAPER trading views.
- [ ] Portfolio, journal, backtest and research UI.

### Phase 9 — Infrastructure
- [ ] PostgreSQL, ClickHouse, Redis and Parquet/object storage.
- [ ] Docker/deployment configuration.
- [ ] Monitoring and operational runbooks.
- [ ] Migrations and reverse proxy.

## Non-negotiable architecture rules
```text
Strategy
  ↓
Probability / Expected Value
  ↓
RiskEngine
  ↓
OMS
  ↓
Execution
```

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

The milestone is complete only when automated tests cover the complete flow and it runs without live order execution.

## Current next task
Implement the **Upstox adapter boundary and authentication/token lifecycle interfaces** without embedding secrets or broker-specific assumptions into domain code. Then add a deterministic mock adapter test before any real WebSocket connectivity is introduced.
