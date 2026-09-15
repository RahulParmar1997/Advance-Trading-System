# Redis Hot-State Boundary

Redis is an ephemeral acceleration layer. It is never the source of truth for orders, fills, positions, risk decisions, or journal history. PostgreSQL remains authoritative for operational state.

## Allowed uses

- Market-data freshness markers
- Short-lived distributed locks
- Rate-limit state
- Derived cache entries
- Other explicitly TTL-bound ephemeral state

## Required semantics

- Every key must have an explicit namespace.
- Expiring state should use a positive TTL.
- Redis failures must not silently promote cached state to execution authority.
- Keys beginning with `order:` or `position:` are rejected by the application adapter.
- Credentials come from deployment configuration; none are committed to source.
