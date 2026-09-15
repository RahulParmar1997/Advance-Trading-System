-- Initial operational schema. PostgreSQL is the source of truth for execution state.

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    instrument TEXT NOT NULL,
    side TEXT NOT NULL,
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    state TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS fills (
    fill_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    price NUMERIC(24, 10) NOT NULL CHECK (price > 0),
    filled_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS positions (
    instrument TEXT PRIMARY KEY,
    side TEXT NOT NULL,
    quantity BIGINT NOT NULL CHECK (quantity >= 0),
    average_price NUMERIC(24, 10) NOT NULL CHECK (average_price >= 0),
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS fills_order_id_idx ON fills(order_id);
CREATE INDEX IF NOT EXISTS orders_state_updated_at_idx ON orders(state, updated_at);
