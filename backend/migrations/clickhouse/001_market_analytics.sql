-- ClickHouse analytics schema. This store is analytical only and never authorizes execution.

CREATE TABLE IF NOT EXISTS market_events (
    observed_at DateTime64(3, 'UTC'),
    instrument String,
    event_type LowCardinality(String),
    price Decimal(24, 10),
    volume UInt64,
    source LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(observed_at)
ORDER BY (instrument, observed_at);

CREATE TABLE IF NOT EXISTS market_features (
    observed_at DateTime64(3, 'UTC'),
    instrument String,
    timeframe_seconds UInt32,
    feature_name LowCardinality(String),
    feature_value Float64,
    source LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(observed_at)
ORDER BY (instrument, timeframe_seconds, feature_name, observed_at);
