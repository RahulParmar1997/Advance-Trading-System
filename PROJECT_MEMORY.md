# Advance Trading System — Project Memory

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Authoritative branch:** `main` only
**Mode:** PAPER-first; no uncontrolled live execution
**Updated:** 2026-09-15

## Purpose
India-focused Market Intelligence + Quant Research + Automated Trading Platform.

## Architecture invariants
- Market Event → Normalization → Validation → Candle → Features → Market State → Strategy → Opportunity → Probability/EV → RiskEngine → OMS → Paper Fill → Position → P&L → Journal.
- AI must never bypass RiskEngine or place uncontrolled orders.
- Strategy logic must be deterministic, testable, network-independent and database-independent.
- Broker-specific code stays behind adapter boundaries.
- Observed market data must remain distinguishable from model-derived estimates.
- Backtests must be chronology-safe and free of look-ahead bias.
- PAPER remains the default.
- Work directly on `main`; do not create feature branches unless explicitly requested.

## Completed foundation
- Python backend package with pytest/Ruff and GitHub Actions quality workflow.
- Versioned domain contracts and compatibility validation.
- Structured JSON logging with recursive secret redaction.
- Deterministic health/readiness checks.
- Canonical broker-neutral QuoteEvent and market-data normalization.
- Multi-timeframe, session-aware candle engine with volume delta.
- Deterministic data-quality service.
- Versioned/content-addressed instrument-master snapshots and monotonic publication.
- Upstox BOD JSON instrument-master parser/source boundary.
- Upstox V3 protobuf decoder boundary and vendored/pinned schema boundary.
- Real `websockets` transport with injectable connector/decoder.
- India market-session calendar and authoritative market-status contract/source.
- RiskEngine freshness/fail-closed market-status gate.
- Market structure, liquidity, FVG, order-block and regime primitives.
- Unified MarketState foundation.
- Displacement feature engine using only prior completed candles.
- Volume-profile and order-flow analytics with explicit feed-capability boundaries.
- Futures/options contract metadata and option-chain validation.
- Deterministic Black-Scholes option Greeks and implied-volatility solver.
- Deterministic futures basis analytics.
- Deterministic breadth and sector analytics from explicit constituent observations.
- Deterministic sector rotation ranking from constituent returns and optional explicit benchmark return.
- Explicit FII/DII institutional-flow aggregation from observed flow records; no inference from price/volume.
- Explicit MarketContextEngine joining completed-candle regime classification with market-session metadata and rejecting chronology/session/instrument inconsistencies.
- Deterministic Wyckoff-style event features from completed candles and explicit candle volume, including Spring, Upthrust, Sign of Strength, Sign of Weakness and effort/result absorption observations.
- Trade Type and versioned Strategy framework.
- Opportunity, probability and EV primitives.
- Canonical OMS lifecycle and controlled RiskEngine → PAPER OMS flow.
- PAPER fills, position book, reconciliation, journal and RiskSnapshot integration.
- Event-driven backtester with costs, slippage, latency, partial fills and liquidity limits.
- Walk-forward/OOS, Monte Carlo and cost/capacity/regime sensitivity foundations.
- Pattern DNA similarity and leakage-safe ML dataset/calibration primitives.

## Current analytics capability
### Breadth / sectors
`breadth.py` consumes explicit constituent observations containing instrument, sector, timestamp, previous close, close and volume. It derives advance/decline counts, breadth percentage, net breadth, up/down volume and ratios. Sector breadth and rotation are deterministic; rotation can compare sector average constituent return with an explicitly supplied benchmark return. Mixed timestamps and duplicate instruments are rejected.

### Institutional flow
Institutional flow is represented as explicit observed FII/DII net-value inputs. The aggregator only sums those observations. It does not infer institutional activity from price, candle volume or order flow.

### Volume profile
Use completed trade/volume observations only. Price buckets are explicit/configurable. Expose volume-at-price, POC and value-area boundaries. Do not infer tick-level trade distribution from candle range without an explicit approximation contract.

### Order flow
Use explicit trade prints/aggressor information when available. BUY/SELL/UNKNOWN must be represented explicitly. Never claim buyer/seller aggression when the feed does not support it.

### Options
`derivative_analytics.py` provides deterministic European Black-Scholes price/Greeks and bounded implied-volatility solving. Inputs explicitly require spot, strike, time-to-expiry, risk-free rate and volatility; dividend yield is optional. The solver rejects prices below intrinsic value or outside its supported volatility range. These are model analytics, not broker-observed probabilities.

### Futures
`futures_basis()` reports absolute and percentage futures-vs-spot basis from explicit prices. It does not infer carry, funding or fair value without those inputs.

### Market context
`context.py` provides `MarketContextEngine`, which joins `MarketSessionStatus` with `RegimeObservation`. It requires completed candle timestamps to be timezone-aware and chronological, rejects mixed instruments and mixed session dates, and prevents an observation timestamp from preceding the latest completed candle. This keeps session/regime state explicit and safe for downstream scanners/strategies.

### Wyckoff
`wyckoff.py` compares the latest completed candle only with a strictly prior lookback window. It derives spread, body, closing location, prior range high/low, volume ratio, spread ratio and a normalized effort/result ratio. Event classification is deterministic: Spring and Upthrust require range rejection with elevated volume; Signs of Strength/Weakness require directional range breaks with wide spread, favorable close location and elevated volume; absorption requires elevated volume with a small normalized spread result. No future candle is consulted and zero/invalid volume is rejected.

## Pending roadmap
1. Richer scanner result contracts and explanations.
2. Multi-symbol / multi-timeframe scanner orchestration.
3. Evidence-based scoring.
4. Historical/OOS probability calibration and validation.
5. Explanation/audit evidence persistence.
6. Broker reconciliation adapter implementation.
7. Durable journal backend.
8. Next.js/React/TypeScript trading terminal and dashboards.
9. PostgreSQL, ClickHouse, Redis, Parquet/object storage and deployment/observability infrastructure.

## Next implementation rule
When the user says **NEXT**, inspect the repository and implement the next unchecked roadmap item directly on `main`. Add deterministic tests, update `PROJECT_WORK_STATUS.md`, and update this memory file so the next session can resume without reconstructing project state.

## Safety / quality rules for every next step
- No fabricated broker fields, market data, probabilities or execution status.
- Prefer explicit capability/availability contracts over unsupported inference.
- Validate timestamps, instruments, quantities and session metadata.
- Reject malformed or stale data fail-closed where safety is involved.
- Keep broker SDK/protobuf details out of domain logic.
- Add unit tests for happy path, invalid input, chronology/look-ahead and boundary cases.
- Do not mark a task complete until implementation and tests exist in the repository.
- Do not claim CI is green unless the GitHub Actions result has actually been verified.

## CI note
The latest GitHub Actions state is not verified green. The repository must repair and verify the Ruff failure before claiming the quality gate is healthy.
