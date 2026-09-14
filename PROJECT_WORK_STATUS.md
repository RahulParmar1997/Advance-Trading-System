# Advance Trading System — Project Work Status

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Working branch policy:** `main` ONLY
**Execution policy:** PAPER-first; no uncontrolled live execution
**Last updated:** 2026-09-14

## 1. Working Rule

All future implementation work for this project must be performed directly on the **`main` branch** unless the project owner explicitly changes this rule.

Before changing code:

1. Read this file.
2. Read the master blueprint and engineering prompt.
3. Inspect the existing implementation before modifying it.
4. Preserve the Risk Engine → OMS execution gate.
5. Keep PAPER as the default trading mode.
6. Add or update tests with implementation changes.
7. Update this file after meaningful work.

Do not create or use feature branches for normal project implementation unless explicitly requested by the project owner.

## 2. Main Product Goal

Build the India-focused Market Intelligence + Quant Research + Automated Trading Platform described in the project blueprint.

Core flow:

```text
DATA
→ MARKET STATE
→ MARKET INTELLIGENCE
→ REGIME
→ SCANNER
→ TRADE TYPE
→ STRATEGY
→ OPPORTUNITY
→ PROBABILITY
→ EXPECTED VALUE
→ RISK
→ OMS
→ EXECUTION
→ POSITION
→ JOURNAL
→ PATTERN DNA
→ RESEARCH / ML
```

## 3. Done on `main`

### Repository / documentation
- README exists and defines the project mission and PAPER-first execution policy.
- Master market-intelligence/automated-trading blueprint exists.
- Permanent AI engineering prompt exists.
- Product blueprint exists, although its current encoding could not be decoded by the GitHub connector during the audit.
- Intended folder structure is documented.

### Code status
- The production implementation is **not yet present on main** at the time this status file was created.
- The root repository currently contains the documented specifications rather than the full backend/frontend implementation.

## 4. Previously Prototyped — NOT YET ON MAIN

A first PAPER vertical slice was prototyped on a temporary branch named `foundation/paper-vertical-slice`.

It contains an initial implementation of:

- canonical `QuoteEvent`
- canonical `Order`
- PAPER trading mode
- centralized RiskEngine gate
- Paper OMS
- raw quote normalization
- candle engine
- basic candle features
- unit tests for the above

**Important:** this prototype is not considered completed project work because the project policy is now **main-only**. Any useful code from that prototype must be reviewed, tested, and recreated or merged into `main` deliberately. Do not assume the prototype is production-ready.

## 5. Current Pending Work

### Phase 1 — Engineering foundation
- [ ] Establish production backend package structure on `main`.
- [ ] Establish configuration and environment handling.
- [ ] Establish domain contracts and versioning.
- [ ] Establish test conventions and CI.
- [ ] Establish structured logging and health checks.

### Phase 2 — Market data
- [ ] Upstox adapter interfaces.
- [ ] Authentication/token handling.
- [ ] WebSocket market-data ingestion.
- [ ] Reconnect and heartbeat handling.
- [ ] Canonical event normalization.
- [ ] Data-quality validation.
- [ ] Staleness, gaps, ordering and duplicate detection.
- [ ] Instrument master handling.

### Phase 3 — Market state and analytics
- [ ] Candle engine.
- [ ] Feature engine.
- [ ] Market structure.
- [ ] Liquidity detection.
- [ ] Volume profile.
- [ ] Order-flow analytics where feed data supports them.
- [ ] Futures analytics.
- [ ] Options analytics.
- [ ] Breadth and sector intelligence.
- [ ] Market-regime engine.

### Phase 4 — Intelligence and scanning
- [ ] BOS / CHoCH / MSS.
- [ ] Displacement.
- [ ] Liquidity sweeps.
- [ ] Equal highs/lows.
- [ ] FVG / order blocks / supply-demand.
- [ ] Wyckoff features.
- [ ] Typed scanner DSL / AST.
- [ ] Cheap-to-expensive scanner pipeline.

### Phase 5 — Trading decision engine
- [ ] Trade Type framework.
- [ ] Versioned Strategy interface.
- [ ] Strategy registry.
- [ ] Opportunity engine.
- [ ] Evidence-based scoring.
- [ ] Probability model.
- [ ] Expected-value calculation.
- [ ] Explanation engine.

### Phase 6 — Risk and execution
- [ ] Full RiskEngine limits.
- [ ] Position sizing.
- [ ] Exposure controls.
- [ ] Slippage/liquidity checks.
- [ ] Kill switch.
- [ ] OMS state machine.
- [ ] Idempotency.
- [ ] Broker/application reconciliation.
- [ ] Paper execution.
- [ ] Position manager.
- [ ] P&L.
- [ ] Audit trail.

### Phase 7 — Research
- [ ] Event-driven backtester.
- [ ] Realistic fill model.
- [ ] Brokerage/taxes/fees.
- [ ] Slippage and latency.
- [ ] Partial fills and rejected orders.
- [ ] Walk-forward validation.
- [ ] Monte Carlo analysis.
- [ ] Regime and cost sensitivity.
- [ ] Pattern DNA.
- [ ] Similarity search.
- [ ] ML datasets and calibration.

### Phase 8 — Frontend
- [ ] Next.js / React / TypeScript foundation.
- [ ] Trading-terminal layout.
- [ ] Market dashboard.
- [ ] Charts.
- [ ] Scanner UI.
- [ ] Futures/options views.
- [ ] Trading/PAPER UI.
- [ ] Portfolio.
- [ ] Journal.
- [ ] Backtesting.
- [ ] Research UI.

### Phase 9 — Infrastructure
- [ ] PostgreSQL.
- [ ] ClickHouse.
- [ ] Redis.
- [ ] Parquet/object storage.
- [ ] Docker configuration.
- [ ] Monitoring.
- [ ] Reverse proxy.
- [ ] Migrations.
- [ ] Production deployment and operational runbooks.

## 6. Critical Architecture Rules

These are non-negotiable unless the project owner explicitly changes them:

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

- AI must never bypass RiskEngine.
- AI must never place uncontrolled orders.
- Charting is visualization, never the source of truth for orders/positions.
- Strategy calculations must remain deterministic, testable, network-independent and database-independent.
- Broker-specific code belongs behind adapter interfaces.
- Observed market data must be distinguished from model-derived estimates.
- No look-ahead bias in research/backtesting.
- PAPER remains the default until live trading has explicit safety validation.

## 7. Definition of the First Production Milestone

The first major milestone is a complete, testable PAPER vertical slice:

```text
Market Event
→ Normalization
→ Validation
→ Candle
→ Features
→ Market State
→ Strategy
→ Opportunity
→ Probability / EV
→ RiskEngine
→ OMS
→ Paper Fill
→ Position
→ P&L
→ Journal
```

The milestone is complete only when it is covered by automated tests and can run without live order execution.

## 8. How This File Must Be Maintained

After every meaningful implementation session:

- move completed items from **Pending** to **Done**;
- record important architectural decisions;
- record known blockers/issues;
- record the next concrete task;
- keep this file on `main`.

### Next concrete task

Build the production **market-data foundation on `main`**: canonical event contracts → normalization → validation → deterministic candle/feature pipeline, with tests, while keeping all broker-specific integration behind interfaces.
