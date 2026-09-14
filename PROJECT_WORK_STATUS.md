# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-14

## Working rule
All normal implementation is committed directly to `main`. Before changes: inspect current state, preserve `RiskEngine → OMS`, keep PAPER default, add/update tests, and update this file. Do not use feature branches unless the project owner explicitly changes the rule.

## Product goal
Build the India-focused Market Intelligence + Quant Research + Automated Trading Platform defined by the project specifications.

## Current status
The repository has a substantial deterministic PAPER/research foundation. Live broker execution is not enabled by this work. Upstox transport/protobuf boundaries are isolated behind adapters, and the instrument-master update path now has a broker-neutral contract, deterministic validation, content-addressed snapshots and monotonic atomic publication.

## Done on `main`

### Repository foundation
- [x] `PROJECT_WORK_STATUS.md` established as the implementation ledger.
- [x] Backend Python package foundation established.
- [x] Backend `pyproject.toml` and pytest configuration established.
- [x] Backend test CI workflow added for pushes to `main` and pull requests.
- [x] Domain / ingestion / market package boundaries established.
- [x] Core domain contract version registry established with explicit supported versions.
- [x] QuoteEvent, Opportunity, OMS Order and BacktestEvent contracts carry explicit schema versions.
- [x] Contract versions are validated at domain boundaries and remain distinct from strategy versions and OMS lifecycle transition counters.
- [x] Existing positional constructors remain backward-compatible through version-1 defaults.
- [x] Contract-version compatibility and rejection tests added.
- [x] Structured JSON logging foundation added with deterministic fields.
- [x] Sensitive logging context is recursively redacted for tokens, secrets, passwords, authorization and API keys.
- [x] Structured logging configuration is idempotent and process-safe for repeated setup calls.
- [x] Structured logging tests cover JSON output, context and secret redaction.
- [x] Deterministic health/readiness boundary added with explicit dependency checks.
- [x] Readiness fails closed when dependencies are missing or unhealthy.
- [x] Health-check exceptions expose only exception type, not connection or credential details.
- [x] Health/readiness unit tests added for healthy, unhealthy, exception and deterministic ordering cases.
- [x] Backend development quality tooling defined in `pyproject.toml`.
- [x] CI installs development tooling, runs Ruff linting and executes the backend pytest suite.
- [x] CI permissions are explicitly read-only for repository contents.

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

### Instrument master
- [x] Broker-neutral `InstrumentMasterRecord` identity contract with exchange, symbol, asset type and tradability.
- [x] Deterministic instrument validation and duplicate-identity rejection.
- [x] Versioned, sorted and content-addressed `InstrumentMasterSnapshot`.
- [x] Monotonic snapshot publication through an injected repository boundary.
- [x] Empty/invalid update batches fail closed without replacing the current snapshot.
- [x] Instrument-master updater and validation unit tests.

### Upstox integration foundation
- [x] Upstox-specific adapter package created outside domain code.
- [x] Access-token value/expiry contract.
- [x] TokenProvider and OAuth exchange/refresh interfaces.
- [x] Runtime-only Upstox settings from environment variables.
- [x] Injectable OAuth HTTP client implementation.
- [x] Process-local token-store abstraction for PAPER/testing.
- [x] Production-safe secret-backed token-store abstraction with injected secret-manager boundary.
- [x] Secret-backed token serialization is versioned, expiry-aware and fails closed on malformed/unsupported data.
- [x] Secret-backed token storage has no filesystem or environment-variable persistence fallback.
- [x] Secret-store tests cover round-trip, expiry, clear, missing secret and fail-closed validation paths.
- [x] Upstox market-data client protocol.
- [x] Injectable WebSocket transport boundary.
- [x] Bounded exponential reconnect policy.
- [x] Heartbeat/ping loop abstraction.
- [x] Sequence-aware feed validation.
- [x] Concrete `websockets`-backed transport with injectable connector and protobuf decoder boundary.
- [x] WebSocket authentication, subscription, receive/decode, ping and close behavior covered by deterministic tests.
- [x] Optional `websockets` dependency isolated behind the live transport extra.
- [x] Injectable Upstox V3 protobuf decoder boundary and explicit pinned package/module identifiers.
- [x] Protobuf runtime dependency isolated behind the live extra.
- [x] Protobuf decoder tests cover payload validation and parser-error sanitization.
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
- [x] Strategy → Opportunity → RiskEngine → OMS integration boundary for historical decisions.
- [x] Risk-approved opportunities transition through canonical OMS states before simulated execution.
- [x] Risk-rejected opportunities are recorded as rejected and never reach simulated execution.
- [x] Walk-forward train/test window contracts with chronological, disjoint OOS boundaries.
- [x] Walk-forward runner keeps training data separate from the backtest test window.
- [x] Deterministic Monte Carlo trade-P&L resampling with seeded simulations.
- [x] Monte Carlo summary includes mean, median, worst, best and loss probability.
- [x] Fee/cost sensitivity across explicit fee assumptions.
- [x] Capacity sensitivity across explicit market-participation limits.
- [x] Regime sensitivity aggregates observed trade P&L by caller-supplied regime labels without inferring regimes from outcomes.
- [x] Unit tests for walk-forward and sensitivity analysis.
- [x] Deterministic Pattern DNA feature-vector contract.
- [x] Pattern similarity distance/search with deterministic tie-breaking.
- [x] Outcome summaries use only explicitly observed outcomes and never infer missing labels.
- [x] Pattern DNA unit tests.
- [x] Leakage-safe ML dataset row contract with explicit train/validation/test splits.
- [x] Feature-matrix extraction with schema validation.
- [x] Deterministic probability calibration bins over explicit predictions/outcomes.
- [x] ML dataset and calibration unit tests.
- [x] Historical liquidity contract with execution-time available quantity and market volume.
- [x] Deterministic participation-rate caps using only execution-event observations.
- [x] Explicit no-liquidity and participation-limit rejection reasons.
- [x] Backtester integration for observable partial fills and liquidity-limited execution.
- [x] Historical-liquidity unit tests.

## Pending work

### Phase 1 — Engineering foundation
- [x] Domain contract versioning.
- [x] Structured logging.
- [x] Health/readiness checks.
- [x] Broader CI quality gates.

### Phase 2 — Market data
- [x] Production-safe secret-backed token store abstraction.
- [x] Real WebSocket library transport implementation.
- [x] Upstox V3 protobuf decoder boundary and package/version identifiers.
- [x] Production instrument-master ingestion/update contract and safe snapshot publication foundation.
- [ ] Vendor/pin the actual generated Upstox V3 protobuf module artifact.
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
- [x] Walk-forward/OOS split foundation.
- [x] Monte Carlo and regime/cost/capacity sensitivity foundation.
- [x] Pattern DNA / similarity search foundation.
- [x] ML dataset generation and probability-calibration primitives.
- [x] More realistic historical liquidity/rejection modeling.

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
Fix and verify the existing WebSocket transport test/development dependency mismatch, then continue with **production market-session/status integration**. Keep all work directly on `main`.
