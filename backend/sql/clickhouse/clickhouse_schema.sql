-- ClickHouse Schema for Zero-Shot Analysis Results
-- Optimized for analytical queries and time-series analysis

-- Create database
CREATE DATABASE IF NOT EXISTS `clickhouse-topic-analyzer`;
USE `clickhouse-topic-analyzer`;

-- Main analysis results table
CREATE TABLE zero_shot_analysis (
    -- Primary identifiers
    id UUID DEFAULT generateUUIDv4(),
    content_hash String,  -- Hash of original content for deduplication
    source_url String,
    source_file String,
    
    -- Timestamps (ClickHouse loves DateTime columns)
    crawled_at DateTime,
    analyzed_at DateTime DEFAULT now(),
    
    -- Content metadata
    content_title String,
    content_text String,
    content_length UInt32,
    
    -- Zero-shot analysis results
    specific_topic String,
    broad_category LowCardinality(String),  -- Limited set, use LowCardinality
    marketing_intent LowCardinality(String),
    confidence_score Float32,
    
    -- Business context (array for multiple contexts)
    business_contexts Array(LowCardinality(String)),
    
    -- Trend signals
    trend_signals Array(String),
    
    -- Analysis metadata
    model_name LowCardinality(String) DEFAULT 'facebook/bart-large-mnli',
    processing_time_ms UInt32
    
) ENGINE = MergeTree()
ORDER BY (analyzed_at, broad_category, confidence_score)
PARTITION BY toYYYYMM(analyzed_at)
SETTINGS index_granularity = 8192;

-- Entities table (separate for better normalization)
CREATE TABLE zero_shot_entities (
    -- Links back to main analysis
    analysis_id UUID,
    
    -- Entity details
    entity_name String,
    entity_type LowCardinality(String),
    confidence Float32,
    relevance_score Float32,
    context_snippet String,
    
    -- Timestamps
    extracted_at DateTime DEFAULT now()
    
) ENGINE = MergeTree()
ORDER BY (analysis_id, entity_type, relevance_score)
PARTITION BY toYYYYMM(extracted_at);

-- Trends analysis table
CREATE TABLE zero_shot_trends (
    id UUID DEFAULT generateUUIDv4(),
    
    -- Trend identification
    topic String,
    trend_type LowCardinality(String),  -- emerging, growing, stable, declining
    momentum_score Float32,
    
    -- Trend metadata
    entity_signals Array(String),
    content_examples Array(String),
    business_impact String,
    recommended_actions Array(String),
    
    -- Analysis details
    confidence Float32,
    mentions_count UInt32,
    time_window_hours UInt16,
    
    -- Timestamps
    trend_detected_at DateTime DEFAULT now(),
    trend_period_start DateTime,
    trend_period_end DateTime
    
) ENGINE = MergeTree()
ORDER BY (trend_detected_at, momentum_score, trend_type)
PARTITION BY toYYYYMM(trend_detected_at);

-- Content sources tracking
CREATE TABLE content_sources (
    source_url String,
    domain String,
    source_type LowCardinality(String),  -- website, reddit, twitter, etc.
    
    -- Crawling stats
    first_crawled DateTime,
    last_crawled DateTime,
    crawl_count UInt32,
    success_rate Float32,
    
    -- Content stats
    total_content_items UInt32,
    avg_analysis_confidence Float32
    
) ENGINE = ReplacingMergeTree()
ORDER BY source_url;

-- Daily aggregation materialized view for zero-shot analysis
CREATE MATERIALIZED VIEW daily_analysis_stats
ENGINE = AggregatingMergeTree()
ORDER BY (analysis_date, broad_category)
POPULATE AS
SELECT
    toDate(analyzed_at) as analysis_date,
    broad_category,
    marketing_intent,
    
    -- Aggregations
    count() as total_analyses,
    avg(confidence_score) as avg_confidence,
    uniq(specific_topic) as unique_topics,
    groupArray(specific_topic) as top_topics,
    
    -- Business context distribution
    arrayReduce('groupUniqArray', arrayFlatten(groupArray(business_contexts))) as all_contexts
    
FROM zero_shot_analysis
GROUP BY analysis_date, broad_category, marketing_intent;

-- Google Trends daily summary materialized view
CREATE MATERIALIZED VIEW google_trends_daily_summary
ENGINE = AggregatingMergeTree()
ORDER BY (trend_date, geo, category_name)
POPULATE AS
SELECT
    toDate(crawled_at) as trend_date,
    geo,
    category_name,
    search_type,
    
    -- Aggregations
    count() as total_trends,
    uniq(topic) as unique_topics,
    groupArray(topic) as trending_topics,
    
    -- Interest metrics (for keyword trends with data)
    avg(data_points) as avg_data_points,
    countIf(data_points > 0) as trends_with_data,
    
    -- Marketing relevance
    countIf(marketing_relevance = true) as marketing_relevant_count,
    avg(CASE WHEN marketing_relevance = true THEN 1.0 ELSE 0.0 END) as marketing_relevance_rate
    
FROM google_trends
GROUP BY trend_date, geo, category_name, search_type;

-- Cross-source topic correlation materialized view
CREATE MATERIALIZED VIEW cross_source_topic_correlation
ENGINE = AggregatingMergeTree()
ORDER BY (analysis_date, normalized_topic)
POPULATE AS
SELECT
    toDate(COALESCE(za.analyzed_at, gt.crawled_at)) as analysis_date,
    
    -- Normalized topic name for cross-source matching
    CASE 
        WHEN za.specific_topic != '' THEN lower(za.specific_topic)
        WHEN gt.topic != '' THEN lower(gt.topic)
        ELSE 'unknown'
    END as normalized_topic,
    
    -- Source tracking
    multiIf(
        za.id IS NOT NULL AND gt.id IS NOT NULL, 'both',
        za.id IS NOT NULL, 'zero_shot',
        gt.id IS NOT NULL, 'google_trends',
        'unknown'
    ) as source_combination,
    
    -- Metrics from zero-shot analysis
    countIf(za.id IS NOT NULL) as zero_shot_mentions,
    avgIf(za.confidence_score, za.id IS NOT NULL) as avg_zero_shot_confidence,
    groupArrayIf(za.broad_category, za.id IS NOT NULL AND za.broad_category != '') as zero_shot_categories,
    
    -- Metrics from Google Trends
    countIf(gt.id IS NOT NULL) as google_trends_mentions,
    groupArrayIf(gt.geo, gt.id IS NOT NULL) as google_trends_geos,
    groupArrayIf(gt.category_name, gt.id IS NOT NULL AND gt.category_name != '') as google_categories,
    
    -- Cross-source correlation strength
    CASE 
        WHEN za.id IS NOT NULL AND gt.id IS NOT NULL THEN 'high'
        WHEN (countIf(za.id IS NOT NULL) > 0 AND countIf(gt.id IS NOT NULL) > 0) THEN 'medium'
        ELSE 'low'
    END as correlation_strength
    
FROM zero_shot_analysis za
FULL OUTER JOIN google_trends gt ON (
    lower(za.specific_topic) = lower(gt.topic) 
    AND toDate(za.analyzed_at) = toDate(gt.crawled_at)
)
WHERE (za.specific_topic != '' OR gt.topic != '')
GROUP BY analysis_date, normalized_topic, source_combination;

-- Daily trending insights across all sources (excluding X.com)
CREATE MATERIALIZED VIEW daily_trending_insights
ENGINE = AggregatingMergeTree()
ORDER BY (trend_date, trend_strength)
POPULATE AS
SELECT
    toDate(GREATEST(
        COALESCE(za.analyzed_at, toDateTime('1900-01-01')),
        COALESCE(gt.crawled_at, toDateTime('1900-01-01'))
    )) as trend_date,
    
    -- Topic identification
    COALESCE(
        nullIf(za.specific_topic, ''),
        nullIf(gt.topic, ''),
        'unknown_topic'
    ) as topic,
    
    -- Trend strength calculation
    multiIf(
        za.id IS NOT NULL AND gt.id IS NOT NULL, 'very_high',
        (za.confidence_score >= 0.8 OR gt.marketing_relevance = true), 'high',
        (za.confidence_score >= 0.6 OR gt.data_points > 10), 'medium',
        'low'
    ) as trend_strength,
    
    -- Source diversity
    multiIf(
        za.id IS NOT NULL AND gt.id IS NOT NULL, 'multi_source',
        za.id IS NOT NULL, 'content_analysis',
        gt.id IS NOT NULL, 'search_trends',
        'unknown'
    ) as source_type,
    
    -- Aggregated metrics
    count() as total_mentions,
    countIf(za.id IS NOT NULL) as content_mentions,
    countIf(gt.id IS NOT NULL) as search_mentions,
    
    -- Content analysis insights
    avgIf(za.confidence_score, za.id IS NOT NULL) as avg_content_confidence,
    groupArrayIf(za.broad_category, za.id IS NOT NULL AND za.broad_category != '') as content_categories,
    groupArrayIf(za.marketing_intent, za.id IS NOT NULL AND za.marketing_intent != '') as marketing_intents,
    
    -- Search trends insights
    groupArrayIf(gt.geo, gt.id IS NOT NULL) as search_geos,
    groupArrayIf(gt.category_name, gt.id IS NOT NULL AND gt.category_name != '') as search_categories,
    avgIf(gt.data_points, gt.id IS NOT NULL AND gt.data_points > 0) as avg_search_data_points,
    
    -- Business context
    arrayReduce('groupUniqArray', arrayFlatten(groupArrayIf(za.business_contexts, za.id IS NOT NULL))) as all_business_contexts
    
FROM zero_shot_analysis za
FULL OUTER JOIN google_trends gt ON (
    lower(za.specific_topic) = lower(gt.topic)
    AND abs(toUnixTimestamp(za.analyzed_at) - toUnixTimestamp(gt.crawled_at)) <= 86400
)
WHERE (
    (za.specific_topic != '' AND za.confidence_score >= 0.5) 
    OR 
    (gt.topic != '' AND (gt.marketing_relevance = true OR gt.data_points > 0))
)
GROUP BY trend_date, topic, trend_strength, source_type;

-- X.com trending topics table
CREATE TABLE x_trending_topics (
    id UUID DEFAULT generateUUIDv4(),
    
    -- Trending topic details
    topic String,
    hashtag String,
    trend_rank UInt8,
    tweet_volume Nullable(UInt64),
    location LowCardinality(String),
    
    -- Social media metrics
    virality_score Float32,
    marketing_potential LowCardinality(String),  -- high, medium, low
    brand_safety LowCardinality(String),         -- safe, medium_risk, high_risk, unknown
    social_category LowCardinality(String),      -- social_media_native, technology_innovation, etc.
    
    -- Analysis results (links to zero_shot_analysis)
    analysis_id Nullable(UUID),
    
    -- Demographics and targeting
    target_demographics Array(String),
    marketing_actions Array(String),
    
    -- Source tracking
    source_method LowCardinality(String),        -- api, web_scraping, third_party
    source_url String,
    promoted Bool DEFAULT false,
    
    -- Timestamps
    trending_at DateTime,
    crawled_at DateTime DEFAULT now(),
    analyzed_at Nullable(DateTime)
    
) ENGINE = MergeTree()
ORDER BY (trending_at, trend_rank, marketing_potential)
PARTITION BY toYYYYMM(trending_at)
SETTINGS index_granularity = 8192;

-- X.com trending analysis summary (materialized view)
CREATE MATERIALIZED VIEW x_trending_daily_summary
ENGINE = AggregatingMergeTree()
ORDER BY (trend_date, marketing_potential)
POPULATE AS
SELECT
    toDate(trending_at) as trend_date,
    marketing_potential,
    social_category,
    location,
    
    -- Aggregations
    count() as total_trends,
    avg(virality_score) as avg_virality,
    sum(CASE WHEN tweet_volume IS NOT NULL THEN tweet_volume ELSE 0 END) as total_volume,
    groupArray(topic) as trending_topics,
    
    -- Top trends by category
    argMax(topic, virality_score) as top_viral_topic,
    argMax(topic, tweet_volume) as top_volume_topic
    
FROM x_trending_topics
GROUP BY trend_date, marketing_potential, social_category, location;

-- Indexes for common queries
-- ALTER TABLE zero_shot_analysis ADD INDEX idx_confidence confidence_score TYPE minmax GRANULARITY 4;
-- ALTER TABLE zero_shot_analysis ADD INDEX idx_topic specific_topic TYPE bloom_filter GRANULARITY 1;
-- ALTER TABLE zero_shot_entities ADD INDEX idx_entity_name entity_name TYPE bloom_filter GRANULARITY 1;
-- ALTER TABLE x_trending_topics ADD INDEX idx_topic topic TYPE bloom_filter GRANULARITY 1;
-- ALTER TABLE x_trending_topics ADD INDEX idx_hashtag hashtag TYPE bloom_filter GRANULARITY 1;

-- Google Trends data table
CREATE TABLE google_trends (
    id UUID DEFAULT generateUUIDv4(),
    
    -- Topic details
    topic String,
    geo LowCardinality(String),
    timeframe LowCardinality(String),
    
    -- Google category information
    category_id Int32 DEFAULT 0,  -- 0 for "All categories", removed nullable
    category_name LowCardinality(String),
    
    -- Search data
    search_type LowCardinality(String),  -- trending, keyword
    trend_rank Nullable(UInt8),
    
    -- Time series data (stored as JSON string)
    interest_over_time String,  -- JSON array of interest values
    time_index String,          -- JSON array of timestamps
    data_points UInt16,
    
    -- Meta information
    source LowCardinality(String),
    marketing_relevance Bool DEFAULT false,
    
    -- Timestamps
    crawled_at DateTime DEFAULT now(),
    trend_timestamp DateTime
    
) ENGINE = MergeTree()
ORDER BY (crawled_at, geo, category_id, search_type)
PARTITION BY toYYYYMM(crawled_at)
SETTINGS index_granularity = 8192;

-- Google Trends related queries table
CREATE TABLE google_trends_related (
    id UUID DEFAULT generateUUIDv4(),
    
    -- Main topic
    main_topic String,
    geo LowCardinality(String),
    
    -- Related query details
    related_query String,
    query_type LowCardinality(String),  -- rising, top
    
    -- Timestamps
    crawled_at DateTime DEFAULT now()
    
) ENGINE = MergeTree()
ORDER BY (crawled_at, main_topic, query_type)
PARTITION BY toYYYYMM(crawled_at);

-- ALTER TABLE google_trends ADD INDEX idx_topic topic TYPE bloom_filter GRANULARITY 1;
-- ALTER TABLE google_trends ADD INDEX idx_category category_name TYPE bloom_filter GRANULARITY 1;

-- Sample queries for testing:
/*
-- Top topics by confidence
SELECT specific_topic, avg(confidence_score) as avg_conf, count() as mentions
FROM zero_shot_analysis 
WHERE analyzed_at >= now() - INTERVAL 7 DAY
GROUP BY specific_topic
ORDER BY avg_conf DESC, mentions DESC
LIMIT 10;

-- Trend analysis over time
SELECT 
    toDate(analyzed_at) as date,
    broad_category,
    count() as daily_count,
    avg(confidence_score) as avg_confidence
FROM zero_shot_analysis 
GROUP BY date, broad_category
ORDER BY date DESC, daily_count DESC;

-- Entity popularity
SELECT 
    e.entity_name,
    e.entity_type,
    count() as mentions,
    avg(e.relevance_score) as avg_relevance,
    groupArray(DISTINCT a.broad_category) as categories
FROM zero_shot_entities e
LEFT JOIN zero_shot_analysis a ON e.analysis_id = a.id
WHERE e.extracted_at >= now() - INTERVAL 30 DAY
GROUP BY e.entity_name, e.entity_type
HAVING mentions >= 3
ORDER BY avg_relevance DESC, mentions DESC;

-- Trending topics detection
SELECT 
    specific_topic,
    count() as current_week,
    countIf(analyzed_at >= now() - INTERVAL 14 DAY AND analyzed_at < now() - INTERVAL 7 DAY) as prev_week,
    (current_week - prev_week) / prev_week * 100 as growth_percent
FROM zero_shot_analysis
WHERE analyzed_at >= now() - INTERVAL 14 DAY
GROUP BY specific_topic
HAVING current_week >= 5 AND prev_week >= 2
ORDER BY growth_percent DESC;

-- X.com trending analysis queries

-- High-potential marketing trends from X.com
SELECT 
    topic,
    hashtag,
    trend_rank,
    tweet_volume,
    virality_score,
    marketing_potential,
    brand_safety,
    social_category,
    target_demographics,
    marketing_actions[1] as top_action
FROM x_trending_topics 
WHERE marketing_potential = 'high' 
  AND brand_safety IN ('safe', 'unknown')
  AND trending_at >= now() - INTERVAL 24 HOUR
ORDER BY virality_score DESC, tweet_volume DESC
LIMIT 10;

-- Cross-platform trend correlation
SELECT 
    x.topic as x_topic,
    a.specific_topic as analysis_topic,
    x.virality_score,
    a.confidence_score,
    x.marketing_potential,
    a.marketing_intent
FROM x_trending_topics x
LEFT JOIN zero_shot_analysis a ON x.analysis_id = a.id
WHERE x.marketing_potential IN ('high', 'medium')
  AND a.confidence_score > 0.7
ORDER BY x.virality_score DESC;

-- Daily trending topics summary
SELECT 
    trend_date,
    marketing_potential,
    social_category,
    count() as trend_count,
    avg(avg_virality) as avg_virality_score,
    groupArray(top_viral_topic)[1] as most_viral_topic
FROM x_trending_daily_summary
WHERE trend_date >= today() - 7
GROUP BY trend_date, marketing_potential, social_category
ORDER BY trend_date DESC, avg_virality_score DESC;

-- Brand safety analysis
SELECT 
    brand_safety,
    count() as trend_count,
    avg(virality_score) as avg_virality,
    groupArray(topic) as sample_topics
FROM x_trending_topics
WHERE trending_at >= now() - INTERVAL 24 HOUR
GROUP BY brand_safety
ORDER BY trend_count DESC;
*/