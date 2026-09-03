-- Kernel Panic Analysis - ClickHouse Schema
-- Futtasd ezt a szkriptet a ClickHouse elindítása után

-- Adatbázis létrehozása
CREATE DATABASE IF NOT EXISTS kernel_events;
CREATE DATABASE IF NOT EXISTS kernel_alerts;

-- Kernel események tábla
CREATE TABLE IF NOT EXISTS kernel_events.kernel_events (
    timestamp DateTime64(9),
    pid UInt32,
    tid UInt32,
    cpu UInt8,
    event_type String,
    duration_ns UInt64,
    retval Int32,
    comm String,
    -- Metaadatok
    host String DEFAULT '',
    kernel_version String DEFAULT '',
    -- Egyedi azonosító
    event_id UUID DEFAULT generateUUIDv4(),
    -- Particionálás idő alapján
    date Date DEFAULT toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, pid, event_type)
SETTINGS index_granularity = 8192;

-- Riasztások tábla
CREATE TABLE IF NOT EXISTS kernel_alerts.kernel_alerts (
    timestamp DateTime64(9),
    alert_level String,
    panic_probability Float64,
    events String,
    -- Metaadatok
    host String DEFAULT '',
    model_version String DEFAULT '',
    -- Egyedi azonosító
    alert_id UUID DEFAULT generateUUIDv4(),
    -- Particionálás idő alapján
    date Date DEFAULT toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, alert_level)
SETTINGS index_granularity = 8192;

-- Anomália események tábla
CREATE TABLE IF NOT EXISTS kernel_alerts.anomalies (
    timestamp DateTime64(9),
    pid UInt32,
    event_type String,
    anomaly_score Float64,
    is_anomaly UInt8,
    -- Metaadatok
    host String DEFAULT '',
    model_version String DEFAULT '',
    date Date DEFAULT toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, anomaly_score)
SETTINGS index_granularity = 8192;

-- Materialized view: per-second event count
CREATE MATERIALIZED VIEW IF NOT EXISTS kernel_events.events_per_second
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(time)
ORDER BY (time)
AS SELECT
    toStartOfSecond(timestamp) AS time,
    count() AS event_count,
    countDistinct(pid) AS unique_pids
FROM kernel_events.kernel_events
GROUP BY time;

-- Materialized view: per-minute alert count
CREATE MATERIALIZED VIEW IF NOT EXISTS kernel_alerts.alerts_per_minute
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(time)
ORDER BY (time)
AS SELECT
    toStartOfMinute(timestamp) AS time,
    count() AS alert_count,
    countIf(alert_level = 'CRITICAL') AS critical_count,
    countIf(alert_level = 'HIGH') AS high_count,
    countIf(alert_level = 'MEDIUM') AS medium_count,
    countIf(alert_level = 'LOW') AS low_count
FROM kernel_alerts.kernel_alerts
GROUP BY time;

-- Indexek teljesítmény optimalizáláshoz
CREATE INDEX IF NOT EXISTS idx_event_type ON kernel_events.kernel_events (event_type) TYPE bloom_filter GRANULARITY 4;
CREATE INDEX IF NOT EXISTS idx_pid ON kernel_events.kernel_events (pid) TYPE minmax GRANULARITY 4;
CREATE INDEX IF NOT EXISTS idx_alert_level ON kernel_alerts.kernel_alerts (alert_level) TYPE bloom_filter GRANULARITY 4;

-- Nézetek gyakori lekérdezésekhez
CREATE VIEW IF NOT EXISTS kernel_events.recent_events AS
SELECT *
FROM kernel_events.kernel_events
WHERE timestamp > now() - INTERVAL 1 HOUR
ORDER BY timestamp DESC
LIMIT 1000;

CREATE VIEW IF NOT EXISTS kernel_alerts.recent_alerts AS
SELECT *
FROM kernel_alerts.kernel_alerts
WHERE timestamp > now() - INTERVAL 1 HOUR
ORDER BY timestamp DESC
LIMIT 100;
