# Advance Trading System — Project Memory

**Repository:** `RahulParmar1997/Advance-Trading-System`
**Authoritative branch:** `main` only
**Mode:** PAPER-first; no uncontrolled live execution
**Updated:** 2026-09-16

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
- Deterministic Wyckoff-style event features from completed candles and explicit candle volume.
- Rich scanner result contract with explicit evidence and deterministic explanations.
- Multi-symbol / multi-timeframe scanner orchestration with explicit scope identity and deterministic ordering.
- Deterministic evidence-based scanner scoring.
- Historical probability calibration and leakage-safe OOS validation.
- Immutable append-only audit evidence persistence for scanner, scoring, probability and risk decisions.
- Upstox broker reconciliation adapter translating authoritative order/fill responses into broker-neutral snapshots and fills with identity and timestamp validation.

## Durable journal backend
`journal/durable.py` provides `JsonlAuditJournal` and `JournalCheckpoint`. The journal is append-only and persists one validated `AuditEvent` per JSONL record. Startup reload validates every record and rejects malformed or duplicate entries fail-closed. Appends flush the record before updating in-memory indexes. Checkpoints expose event count and last event id without adding execution capability. This backend is intended for PAPER/local durability and remains separate from broker execution authority; a database-backed production journal can replace it behind the same conceptual boundary.

## Audit evidence persistence
`audit/evidence.py` defines immutable, content-addressed audit records for scanner, score, probability and risk decisions. Audit evidence is observational provenance only and cannot authorize or submit orders.

## Broker reconciliation adapter
`reconciliation/upstox.py` defines `UpstoxReconciliationAdapter` behind an injected `UpstoxOrderApi`. It translates authoritative broker order details/fills into broker-neutral contracts and rejects identity/timestamp/quantity errors. It has no order-submission capability.

## Persistence / execution hardening
- PostgreSQL operational adapter has explicit pooled connection lifecycle with acquired connections returned to the pool exactly once.
- `AsyncpgConnectionFactory` serializes lazy pool creation so concurrent first callers share one pool instead of racing to create multiple pools.
- PAPER OMS idempotency fails closed when a client idempotency key is presented with a different order ID; it never silently replays the original order under a mismatched identity.
- `MigrationRunner` always closes/releases its acquired PostgreSQL migration connection, including migration failure paths.
- `MigrationRunner` executes migration SQL and `schema_migrations` bookkeeping in one transaction so partial migration application rolls back atomically.
- Migration tests cover commit, rollback, idempotency and connection cleanup.
- The `ParquetStore` application protocol matches the concrete immutable adapter's versioned dataset reference, manifest and dataset read/write API, with deterministic runtime conformance coverage.
- PostgreSQL, ClickHouse, Redis and Parquet storage protocols are runtime-checkable, with deterministic tests asserting that all concrete application adapters satisfy their corresponding boundaries.

## Frontend terminal
- The Next.js frontend now provides a dark-first observational overview with Market State, Scanner, Risk and PAPER Portfolio panels, navigation, feed-state messaging and explicit RiskEngine → OMS execution-boundary messaging.
- Responsive terminal styling covers desktop, tablet and mobile widths without adding execution controls.
- A deterministic Node UI-contract test verifies required panels, PAPER mode, disconnected-feed state and safety-boundary messaging.
- Frontend CI now installs dependencies and runs UI contract tests, ESLint, TypeScript typecheck and a production build.
- No live market values are fabricated; the terminal explicitly reports an unconnected feed until typed backend read-only endpoints exist.

## Pending roadmap
1. Typed read-only backend endpoints for the terminal's Market State, Scanner, Risk and Portfolio views.
2. Dedicated frontend routes for market, scanner, risk and portfolio views.
3. Runtime end-to-end monitoring validation outside CI against an actually running deployment environment, if a persistent environment is required.
4. Additional concrete vendor adapter/factory integration coverage when those drivers are introduced.

## Next implementation rule
When the user says **NEXT**, inspect the repository and implement the next unchecked roadmap item directly on `main`. Add deterministic tests, update `PROJECT_WORK_STATUS.md`, and update this memory file so the next session can resume without reconstructing project state.

## Safety / quality rules
- No fabricated broker fields, market data, probabilities or execution status.
- Prefer explicit capability/availability contracts over unsupported inference.
- Validate timestamps, instruments, quantities and session metadata.
- Reject malformed or stale data fail-closed where safety is involved.
- Keep broker SDK/protobuf details out of domain logic.
- Add unit tests for happy path, invalid input, chronology/look-ahead and boundary cases.
- Do not mark a task complete until implementation and tests exist in the repository.
- Do not claim CI is green unless the GitHub Actions result has actually been verified.

## CI note
Run 527 (`35068304434`) on `b77b3f11f2e3b3ff78156ec165dcf152ebdecd30` was the last verified successful run before the frontend changes. The current frontend commits require a new GitHub Actions run before their tests/build can be considered verified.
