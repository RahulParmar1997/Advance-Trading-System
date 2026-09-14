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

### Upstox integration foundation
- [x] Upstox-specific adapter package created outside domain code.
- [x] Access-token value/expiry contract.
- [x] TokenProvider and OAuth exchange/refresh interfaces.
- [x] Runtime-only Upstox settings from environment variables.
- [x] Injectable OAuth HTTP client implementation.
- [x] Process-local token-store abstraction for PAPER/testing.
- [x] Upstox market-data client protocol.
- [x] Injectable WebSocket transport boundary.
- [x] Bounded exponential reconnect policy.
- [x] Heartbeat/ping loop abstraction.
- [x] Sequence-aware feed validation.
- [x] Deterministic OAuth, token-store, sequence and transport tests.
- [x] No credentials or secrets committed.
- [x] Injectable Upstox V3 protobuf decoder boundary.
- [x] Deterministic V3 feed mapper for LTPC/full-feed structures.
- [x] PAPER market-data vertical smoke-test foundation.
- [x] V3 mapper tests for LTPC, bid/ask, volume and invalid payload fields.

### Market state / analytics
- [x] Instrument-master identity/active-state validation foundation.
- [x] India market-session gate foundation with injectable holiday policy.
- [x] Market-structure swings and HH/HL/LH/LL classification.
- [x] BOS / CHoCH / MSS structure observations.
- [x] Liquidity equal-high/equal-low detection.
- [x] Fair-value-gap observations.
- [x] Order-block observations.
- [x] Unified `MarketState` construction.
- [x] Deterministic market-regime classifier: trend up/down, range, transition and insufficient-data states.
- [x] Unit tests for structure, liquidity, unified state and regime behavior.

### Intelligence / scanning
- [x] Typed scanner DSL / AST with deterministic condition evaluation.
- [x] Cheap-first scanner pipeline and deterministic candidate identity.
- [x] Scanner unit tests.

### Trading decision engine
- [x] Trade Type framework and registry.
- [x] Versioned deterministic Strategy interface and registry.
- [x] Breakout-continuation strategy foundation.
- [x] Canonical Opportunity contract with entry, stop, target, direction and R:R.
- [x] Deterministic opportunity identity and auditable explanation.
- [x] Probability baseline estimator with explicit estimate-vs-observation semantics.
- [x] Expected-value calculation in R-multiples.
- [x] Probability/EV unit tests.

### Risk / execution safety
- [x] Production-oriented pre-trade `RiskPolicy` contract.
- [x] `RiskSnapshot` for P&L, exposure, leverage, concurrency and broker health.
- [x] Hard kill-switch and circuit-breaker gates.
- [x] Market-session and stale-data hard stops.
- [x] Strategy validity, Trade Type enablement and duplicate-opportunity gates.
- [x] Daily-loss, strategy-loss, symbol-exposure and portfolio-exposure limits.
- [x] Concurrent-trade and leverage limits.
- [x] Slippage, probability and minimum-R:R gates.
- [x] Explicit order-notional, available-liquidity and market-participation gates.
- [x] Auditable `RiskDecision` with passed-check trace.
- [x] Dedicated RiskEngine safety tests.
- [x] Canonical OMS state machine with monotonic partial/full-fill rules.
- [x] Idempotent PAPER order gateway keyed by client identity.
- [x] Controlled `RiskEngine → PAPER OMS` submission workflow.
- [x] PAPER fill simulator with partial/full fill handling.
- [x] Deterministic position book with average-price, realized-P&L and unrealized-P&L accounting.
- [x] Broker-neutral fill and reconciliation contracts.
- [x] Position manager with duplicate-fill protection.
- [x] Append-only in-memory journal/audit boundary.
- [x] Durable JSONL journal boundary for PAPER/testing.
- [x] Position updates emit auditable lifecycle events.
- [x] PositionBook → RiskSnapshot integration with explicit mark prices and caller-supplied daily/strategy P&L.
- [x] Unit tests for PAPER fills, position manager, capacity gates, reconciliation, journal and RiskSnapshot behavior.

### Research / backtesting
- [x] Deterministic event-driven backtester core.
- [x] Chronological event processing to establish a no-look-ahead execution boundary.
- [x] Strategy protocol isolated from broker/network/database dependencies.
- [x] Simulated execution price with configurable slippage.
- [x] Configurable transaction fees.
- [x] Latency policy and next-observable-event execution boundary.
- [x] Configurable partial-fill quantity policy.
- [x] Mark-to-market ending equity and maximum drawdown tracking.
- [x] Signed position accounting for long and short fills.
- [x] Explicit deterministic rejection policy and insufficient-cash guard.
- [x] Backtest fill and result contracts.
- [x] Unit tests for chronological processing, slippage, fees, latency, partial fills, rejection and round-trip P&L.

## Previously prototyped — not used as the implementation branch
A temporary `foundation/paper-vertical-slice` prototype existed before the main-only rule. Its useful ideas were reviewed and recreated deliberately on `main`; it is not the active development branch.

## Pending work

### Phase 1 — Engineering foundation
- [ ] Domain contract versioning.
- [ ] Structured logging.
- [ ] Health/readiness checks.
- [ ] Broader CI quality gates.

### Phase 2 — Market data
- [ ] Production secret-backed token store.
- [ ] Real WebSocket library transport implementation.
- [ ] Generated Upstox V3 protobuf package/version pinning.
- [ ] Production instrument-master ingestion/update process.
- [ ] Production market-session/status integration.

### Phase 3 — Market state / analytics
- [ ] Multi-timeframe candle/session engine.
- [ ] Expanded feature engine.
- [ ] Displacement and richer structure confirmation.
- [ ] Volume profile/order flow where feed data supports it.
- [ ] Futures/options analytics.
- [ ] Breadth, sector rotation and institutional-flow intelligence.
- [ ] Richer regime/session context integration into `MarketState`.

### Phase 4 — Intelligence / scanning
- [ ] Wyckoff features.
- [ ] Scanner result contracts and richer explanations.
- [ ] Multi-symbol / multi-timeframe scanner orchestration.

### Phase 5 — Trading decision engine
- [ ] Evidence-based scoring layer.
- [ ] Historical probability calibration.
- [ ] Out-of-sample probability validation.
- [ ] Explanation/audit evidence persistence.

### Phase 6 — Risk / execution
- [ ] Broker reconciliation adapter implementation.
- [ ] Stronger durable journal backend.

### Phase 7 — Research
- [ ] Connect existing Strategy/Opportunity/RiskEngine/OMS contracts into backtester.
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
  ↓
Position / P&L
  ↓
Journal / Audit
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
Connect the existing **Strategy → Opportunity → RiskEngine → OMS** contracts into the backtester with explicit risk context, canonical OMS state transitions, and rejection reasons, while preserving zero look-ahead.
