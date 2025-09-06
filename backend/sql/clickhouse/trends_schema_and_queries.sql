-- Trends Data Model for ClickHouse
-- Schema and Query Examples

-- Topics Table (assumed existing structure)
-- CREATE TABLE topic (
--     topic_id UInt32,
--     topic_name String,
--     category String,
--     business String,
--     trend_score Float32
-- ) ENGINE = MergeTree()
-- ORDER BY topic_id;

-- Trend Events Table (Denormalized with Geographic Hierarchy)
CREATE TABLE trend_events (
    event_id UInt64,
    topic_id UInt32,
    topic_name LowCardinality(String),  -- denormalized
    category LowCardinality(String),    -- denormalized  
    business LowCardinality(String),    -- denormalized
    timestamp DateTime64(3),
    country_code LowCardinality(String),  -- 'US', 'CA', 'GB'
    region_code LowCardinality(String),   -- 'TX', 'NY', 'ON', 'BC' 
    city_code LowCardinality(String),     -- 'NYC', 'LAX', 'TOR'
    stat_type LowCardinality(String),  -- 'appearance', 'search_volume', 'mentions', etc.
    stat_value Float64,
    trend_score Float32,  -- overall trend strength/momentum
    date Date MATERIALIZED toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (timestamp, country_code, topic_id)
SETTINGS index_granularity = 8192;

-- =============================================
-- TRENDING QUERIES
-- =============================================

-- Trending Topics - Last 24 Hours
SELECT 
    topic_name,
    category,
    business,
    avg(trend_score) as avg_trend_score,
    max(trend_score) as peak_trend_score,
    sum(stat_value) as total_volume
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
GROUP BY topic_id, topic_name, category, business
ORDER BY avg_trend_score DESC
LIMIT 50;

-- Trending Topics - Last 15 Minutes
SELECT 
    topic_name,
    business,
    avg(trend_score) as current_trend_score,
    count(*) as event_count
FROM trend_events
WHERE timestamp >= now() - INTERVAL 15 MINUTE
GROUP BY topic_id, topic_name, business
ORDER BY current_trend_score DESC
LIMIT 20;

-- Trending Topics - Last Few Hours (configurable)
SELECT 
    topic_name,
    category,
    business,
    avg(trend_score) as avg_trend_score,
    max(trend_score) as peak_trend_score
FROM trend_events
WHERE timestamp >= now() - INTERVAL 6 HOUR  -- adjust hours as needed
GROUP BY topic_id, topic_name, category, business
ORDER BY avg_trend_score DESC
LIMIT 30;

-- Trending by Business
SELECT 
    topic_name,
    business,
    avg(trend_score) as trend_score,
    sum(stat_value) as total_volume
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
  AND business = 'tech'  -- replace with desired business
GROUP BY topic_id, topic_name, business
ORDER BY trend_score DESC
LIMIT 25;

-- Trending by Category
SELECT 
    topic_name,
    category,
    avg(trend_score) as trend_score,
    sum(stat_value) as total_volume
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
  AND category = 'sports'  -- replace with desired category
GROUP BY topic_id, topic_name, category
ORDER BY trend_score DESC
LIMIT 25;

-- =============================================
-- ADDITIONAL USEFUL QUERIES
-- =============================================

-- Top trending topics by stat type
SELECT 
    topic_name,
    stat_type,
    avg(trend_score) as avg_trend_score,
    sum(stat_value) as total_stat_value
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
  AND stat_type = 'search_volume'  -- or 'appearance', 'mentions', etc.
GROUP BY topic_id, topic_name, stat_type
ORDER BY avg_trend_score DESC
LIMIT 20;

-- Trending topics by Country
SELECT 
    topic_name,
    country_code,
    avg(trend_score) as avg_trend_score
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
  AND country_code = 'US'  -- replace with desired country
GROUP BY topic_id, topic_name, country_code
ORDER BY avg_trend_score DESC
LIMIT 20;

-- Trending topics by State/Region
SELECT 
    topic_name,
    country_code,
    region_code,
    avg(trend_score) as avg_trend_score
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
  AND country_code = 'US'
  AND region_code = 'CA'  -- replace with desired state
GROUP BY topic_id, topic_name, country_code, region_code
ORDER BY avg_trend_score DESC
LIMIT 20;

-- Trending topics in US and Canada (your specific query)
SELECT 
    topic_name,
    country_code,
    avg(trend_score) as avg_trend_score,
    max(trend_score) as peak_trend_score,
    sum(stat_value) as total_volume,
    count(*) as event_count
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
  AND country_code IN ('US', 'CA')
GROUP BY topic_name, country_code
ORDER BY avg_trend_score DESC
LIMIT 50;