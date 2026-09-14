# Advance Trading System

India-focused Market Intelligence + Quant Research + Automated Trading Platform.

## Blueprint

See [`MARKET_INTELLIGENCE_AUTOMATED_TRADING_MASTER_BLUEPRINT.txt`](./MARKET_INTELLIGENCE_AUTOMATED_TRADING_MASTER_BLUEPRINT.txt) for the master product, workflow, architecture, trading-safety and development specification.

## Code architecture

See [`docs/CODE_ARCHITECTURE.md`](./docs/CODE_ARCHITECTURE.md) for the production-oriented package boundaries and execution flow.

## Current foundation

- Canonical normalized market-event contracts
- PAPER-first trading configuration
- Versioned strategy interface
- Centralized Risk Engine hard gate
- OMS order lifecycle state machine

All execution must remain behind Risk Engine → OMS, with PAPER as the default mode.
