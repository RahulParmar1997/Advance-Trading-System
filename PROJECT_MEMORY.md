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
- Volume-profile and order-flow analytics added where feed capabilities support them.
- Trade Type and versioned Strategy framework.
- Opportunity, probability and EV primitives.
- Canonical OMS lifecycle and controlled RiskEngine → PAPER OMS flow.
- PAPER fills, position book, reconciliation, journal and RiskSnapshot integration.
- Event-driven backtester with costs, slippage, latency, partial fills and liquidity limits.
- Walk-forward/OOS, Monte Carlo and cost/capacity/regime sensitivity foundations.
- Pattern DNA similarity and leakage-safe ML dataset/calibration primitives.

## Current analytics capability
### Volume profile
Use completed trade/volume observations only. Price buckets are explicit/configurable. Expose volume-at-price, POC and value-area boundaries. Do not infer tick-level trade distribution from candle range without an explicit approximation contract.

### Order flow
Use explicit trade prints/aggressor information when available. BUY/SELL/UNKNOWN must be represented explicitly. Never claim buyer/seller aggression when the feed does not support it.

## Pending roadmap
1. Futures/options analytics.
2. Breadth, sector rotation and institutional-flow intelligence.
3. Richer regime/session context integration.
4. Wyckoff features.
5. Richer scanner result contracts and explanations.
6. Multi-symbol / multi-timeframe scanner orchestration.
7. Evidence-based scoring and historical/OOS probability calibration.
8. Explanation/audit evidence persistence.
9. Broker reconciliation adapter implementation.
10. Durable journal backend.
11. Next.js/React/TypeScript trading terminal and dashboards.
12. PostgreSQL, ClickHouse, Redis, Parquet/object storage and deployment/observability infrastructure.

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
