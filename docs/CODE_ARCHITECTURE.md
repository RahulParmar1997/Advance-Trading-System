# Advance Trading System — Code Architecture

This repository follows the Market Intelligence & Automated Trading Platform blueprint.

## Runtime flow

UPSTOX → INGESTION → NORMALIZATION → DATA QUALITY → STORAGE → CANDLE ENGINE → FEATURE ENGINE → MARKET INTELLIGENCE → SCANNER → TRADE TYPE → STRATEGY → OPPORTUNITY → PROBABILITY/EV → RISK ENGINE → OMS → PAPER EXECUTION → POSITION → JOURNAL → PATTERN DNA → RESEARCH/ML

## Package boundaries

- `adapters/`: broker-specific integrations only.
- `ingestion/`: websocket/event intake and reconnect handling.
- `domain/`: canonical domain contracts independent of broker SDKs.
- `market/`: candle and market-state computation.
- `intelligence/`: structure, liquidity, profile and microstructure analytics.
- `scanner/`: typed scanner DSL and staged filtering.
- `trade_types/`: automated-trading selection/filter definitions.
- `strategies/`: deterministic, versioned strategy logic.
- `opportunity/`: scoring, probability and expected-value evaluation.
- `risk/`: mandatory hard gate before OMS.
- `oms/`: order intent/state/reconciliation lifecycle.
- `portfolio/`: positions, P&L and exposure.
- `journal/`: trade outcomes and Pattern DNA.
- `backtest/`: event-driven historical simulation.
- `ml/`: calibrated statistical/ML models.
- `storage/`: Postgres, ClickHouse, Redis and Parquet access.

## Safety boundaries

1. PAPER is the default trading mode.
2. Strategy code must never call a broker adapter directly.
3. AI/ML must never bypass Risk Engine or OMS.
4. Live execution requires explicit production configuration.
5. Broker state is reconciled against OMS; it is not the application source of truth.

## Initial implementation

The repository currently starts with the canonical market-event contract, PAPER-first configuration, versioned strategy interface, centralized risk gate and OMS lifecycle state machine. Additional modules should be added behind these stable boundaries.
