-- ClickHouse Trend Analysis Queries
-- Comprehensive analytics for Google Trends and cross-source trend analysis
-- Based on the content crawler schema with Google Trends mock data

USE `clickhouse-topic-analyzer`;

-- ============================================================================
-- GOOGLE TRENDS ANALYSIS QUERIES
-- ============================================================================

-- 1. Top Trending Topics by Marketing Relevance
-- Shows most relevant marketing trends with data points
SELECT 
    topic,
    geo,
    category_name,
    marketing_relevance,
    data_points,
    toDate(crawled_at) as trend_date,
    search_type
FROM google_trends
WHERE marketing_relevance = true
  AND crawled_at >= now() - INTERVAL 7 DAY
ORDER BY data_points DESC, crawled_at DESC
LIMIT 20;

-- 2. Geographic Trend Distribution Analysis
-- Compare trend adoption across different regions
SELECT 
    geo,
    count() as total_trends,
    countIf(marketing_relevance = true) as marketing_relevant,
    round(marketing_relevant / total_trends * 100, 2) as relevance_percentage,
    avg(data_points) as avg_interest,
    groupArray(topic)[1:5] as top_topics
FROM google_trends
WHERE crawled_at >= now() - INTERVAL 7 DAY
GROUP BY geo
ORDER BY relevance_percentage DESC, avg_interest DESC;

-- 3. Daily Trending Momentum
-- Track daily trend patterns and momentum
SELECT 
    toDate(crawled_at) as date,
    category_name,
    count() as trend_count,
    countIf(data_points > 50) as high_interest_trends,
    countIf(marketing_relevance = true) as marketing_trends,
    avg(data_points) as avg_interest,
    groupArray(topic)[1:3] as top_topics
FROM google_trends
WHERE crawled_at >= now() - INTERVAL 7 DAY
GROUP BY date, category_name
ORDER BY date DESC, trend_count DESC;

-- 4. Category Performance Deep Dive
-- Analyze performance across Google Trends categories
SELECT 
    category_name,
    search_type,
    count() as total_trends,
    avg(data_points) as avg_data_points,
    countIf(marketing_relevance = true) as marketing_trends,
    countIf(data_points > 70) as viral_trends,
    round(marketing_trends / total_trends * 100, 2) as marketing_rate,
    groupArray(topic)[1:3] as sample_topics
FROM google_trends
WHERE crawled_at >= now() - INTERVAL 7 DAY
  AND category_name != ''
GROUP BY category_name, search_type
ORDER BY marketing_trends DESC, avg_data_points DESC;

-- 5. Time Series Interest Analysis with JSON Parsing
-- Extract and analyze time series data from interest_over_time
SELECT 
    topic,
    geo,
    category_name,
    data_points,
    JSONExtract(interest_over_time, 'Array(Int32)') as interest_values,
    JSONExtract(time_index, 'Array(String)') as time_stamps,
    arrayMax(JSONExtract(interest_over_time, 'Array(Int32)')) as peak_interest,
    arrayAvg(JSONExtract(interest_over_time, 'Array(Int32)')) as avg_interest,
    crawled_at
FROM google_trends
WHERE marketing_relevance = true
  AND data_points > 0
  AND crawled_at >= now() - INTERVAL 3 DAY
  AND interest_over_time != ''
ORDER BY peak_interest DESC, data_points DESC
LIMIT 15;

-- ============================================================================
-- CROSS-SOURCE ANALYSIS QUERIES
-- ============================================================================

-- 6. Multi-Source Topic Correlation
-- Find topics mentioned across multiple data sources
SELECT 
    normalized_topic,
    source_combination,
    correlation_strength,
    zero_shot_mentions,
    google_trends_mentions,
    avg_zero_shot_confidence,
    google_trends_geos,
    google_categories,
    analysis_date
FROM cross_source_topic_correlation
WHERE analysis_date >= today() - 7
  AND correlation_strength IN ('high', 'medium')
  AND (zero_shot_mentions > 0 OR google_trends_mentions > 0)
ORDER BY (zero_shot_mentions + google_trends_mentions) DESC, correlation_strength DESC;

-- 7. Daily Trending Insights Comprehensive View
-- Unified view of trending topics across all sources
SELECT 
    trend_date,
    topic,
    trend_strength,
    source_type,
    total_mentions,
    content_mentions,
    search_mentions,
    avg_content_confidence,
    search_geos,
    search_categories,
    all_business_contexts
FROM daily_trending_insights
WHERE trend_date >= today() - 7
  AND trend_strength IN ('very_high', 'high')
  AND topic != 'unknown_topic'
ORDER BY trend_date DESC, total_mentions DESC, trend_strength DESC;

-- ============================================================================
-- ADVANCED ANALYTICS QUERIES
-- ============================================================================

-- 8. Marketing Opportunity Scoring Engine
-- Score trends based on marketing potential and viral characteristics
WITH trend_scores AS (
    SELECT 
        topic,
        geo,
        category_name,
        marketing_relevance,
        data_points,
        search_type,
        toDate(crawled_at) as date,
        CASE 
            WHEN marketing_relevance = true AND data_points > 70 THEN 'high_opportunity'
            WHEN marketing_relevance = true AND data_points > 40 THEN 'medium_opportunity'
            WHEN data_points > 80 THEN 'viral_potential'
            WHEN marketing_relevance = true THEN 'niche_opportunity'
            ELSE 'low_opportunity'
        END as opportunity_score,
        multiIf(
            data_points > 80, 5,
            data_points > 60, 4,
            data_points > 40, 3,
            data_points > 20, 2,
            1
        ) as viral_score
    FROM google_trends
    WHERE crawled_at >= now() - INTERVAL 7 DAY
)
SELECT 
    opportunity_score,
    count() as trend_count,
    avg(data_points) as avg_interest,
    avg(viral_score) as avg_viral_score,
    groupArray(topic)[1:5] as example_topics,
    groupArray(DISTINCT geo) as active_geos,
    groupArray(DISTINCT category_name) as active_categories
FROM trend_scores
WHERE opportunity_score != 'low_opportunity'
GROUP BY opportunity_score
ORDER BY 
    CASE opportunity_score 
        WHEN 'high_opportunity' THEN 1
        WHEN 'viral_potential' THEN 2
        WHEN 'medium_opportunity' THEN 3
        WHEN 'niche_opportunity' THEN 4
        ELSE 5
    END, avg_viral_score DESC;

-- 9. Trend Velocity and Growth Detection
-- Identify trending topics with acceleration patterns
WITH daily_trends AS (
    SELECT 
        topic,
        toDate(crawled_at) as date,
        count() as daily_mentions,
        avg(data_points) as avg_interest,
        max(data_points) as peak_interest
    FROM google_trends
    WHERE crawled_at >= now() - INTERVAL 14 DAY
      AND marketing_relevance = true
    GROUP BY topic, date
    HAVING daily_mentions > 0
),
trend_velocity AS (
    SELECT 
        topic,
        date,
        daily_mentions as current_mentions,
        avg_interest as current_interest,
        lagInFrame(daily_mentions, 1) OVER (PARTITION BY topic ORDER BY date) as prev_mentions,
        lagInFrame(avg_interest, 1) OVER (PARTITION BY topic ORDER BY date) as prev_interest,
        CASE 
            WHEN prev_mentions > 0 THEN (current_mentions - prev_mentions) / prev_mentions * 100
            ELSE 0
        END as mentions_growth,
        CASE 
            WHEN prev_interest > 0 THEN (current_interest - prev_interest) / prev_interest * 100
            ELSE 0
        END as interest_growth
    FROM daily_trends
    WHERE date >= today() - 7
)
SELECT 
    topic,
    date,
    current_mentions,
    round(current_interest, 2) as current_interest,
    round(mentions_growth, 2) as mentions_growth_percent,
    round(interest_growth, 2) as interest_growth_percent,
    multiIf(
        mentions_growth > 100 AND interest_growth > 50, '🚀 Explosive',
        mentions_growth > 50 AND interest_growth > 25, '📈 Accelerating',
        mentions_growth > 20, '⬆️ Growing',
        mentions_growth > 0, '➡️ Stable',
        '📉 Declining'
    ) as trend_direction
FROM trend_velocity
WHERE mentions_growth IS NOT NULL 
  AND (mentions_growth > 20 OR interest_growth > 15)
ORDER BY mentions_growth DESC, interest_growth DESC;

-- 10. Geographic Trend Heat Map Data
-- Generate data for geographic trend visualization
SELECT 
    geo,
    category_name,
    count() as trend_intensity,
    countIf(marketing_relevance = true) as marketing_intensity,
    countIf(data_points > 60) as viral_intensity,
    avg(data_points) as avg_interest_level,
    max(data_points) as peak_interest_level,
    groupArray(topic)[1:5] as trending_topics,
    round(marketing_intensity / trend_intensity * 100, 2) as marketing_percentage
FROM google_trends
WHERE crawled_at >= now() - INTERVAL 7 DAY
  AND geo != ''
GROUP BY geo, category_name
HAVING trend_intensity >= 3  -- Filter out sparse data
ORDER BY trend_intensity DESC, marketing_intensity DESC;

-- ============================================================================
-- MATERIALIZED VIEW QUERIES
-- ============================================================================

-- 11. Google Trends Daily Summary Analytics
-- Query the pre-aggregated daily summary view
SELECT 
    trend_date,
    geo,
    category_name,
    search_type,
    total_trends,
    unique_topics,
    marketing_relevant_count,
    trends_with_data,
    round(marketing_relevance_rate * 100, 2) as marketing_percentage,
    trending_topics[1:5] as top_5_topics
FROM google_trends_daily_summary
WHERE trend_date >= today() - 7
  AND marketing_relevant_count > 0
ORDER BY trend_date DESC, marketing_relevant_count DESC, total_trends DESC;

-- ============================================================================
-- REAL-TIME MONITORING QUERIES
-- ============================================================================

-- 12. Recent High-Impact Trends Dashboard
-- Real-time view of emerging high-impact trends
SELECT 
    topic,
    geo,
    category_name,
    data_points,
    search_type,
    marketing_relevance,
    crawled_at,
    now() - crawled_at as age_minutes,
    multiIf(
        data_points >= 90, '🔥 Viral',
        data_points >= 70, '📈 Hot',
        data_points >= 50, '⭐ Rising', 
        data_points >= 30, '💡 Emerging',
        '🌱 New'
    ) as trend_status,
    multiIf(
        marketing_relevance = true AND data_points > 60, 'IMMEDIATE_ACTION',
        marketing_relevance = true AND data_points > 40, 'MONITOR_CLOSELY',
        data_points > 70, 'VIRAL_WATCH',
        'BACKGROUND'
    ) as action_priority
FROM google_trends
WHERE crawled_at >= now() - INTERVAL 4 HOUR
  AND (marketing_relevance = true OR data_points > 40)
ORDER BY data_points DESC, crawled_at DESC, marketing_relevance DESC;

-- 13. Trend Competition Analysis
-- Find topics trending across multiple geos simultaneously
WITH multi_geo_trends AS (
    SELECT 
        topic,
        count(DISTINCT geo) as geo_count,
        groupArray(DISTINCT geo) as active_geos,
        avg(data_points) as avg_interest,
        max(data_points) as peak_interest,
        sum(data_points) as total_interest,
        countIf(marketing_relevance = true) as marketing_mentions
    FROM google_trends
    WHERE crawled_at >= now() - INTERVAL 24 HOUR
      AND geo != ''
    GROUP BY topic
    HAVING geo_count >= 2  -- Trending in at least 2 geos
)
SELECT 
    topic,
    geo_count,
    active_geos,
    round(avg_interest, 2) as avg_interest,
    peak_interest,
    total_interest,
    marketing_mentions,
    multiIf(
        geo_count >= 4 AND avg_interest > 50, 'GLOBAL_VIRAL',
        geo_count >= 3 AND marketing_mentions > 0, 'REGIONAL_MARKETING',
        geo_count >= 2 AND avg_interest > 60, 'CROSS_BORDER',
        'MULTI_GEO'
    ) as trend_scope
FROM multi_geo_trends
ORDER BY total_interest DESC, geo_count DESC;

-- 14. Category Trend Correlation Matrix
-- Find categories that trend together
WITH category_pairs AS (
    SELECT 
        a.category_name as category_a,
        b.category_name as category_b,
        count() as co_occurrence,
        avg(a.data_points + b.data_points) as combined_interest
    FROM google_trends a
    JOIN google_trends b ON (
        toDate(a.crawled_at) = toDate(b.crawled_at)
        AND a.geo = b.geo
        AND a.category_name != b.category_name
        AND a.category_name < b.category_name  -- Avoid duplicates
    )
    WHERE a.crawled_at >= now() - INTERVAL 7 DAY
      AND a.marketing_relevance = true
      AND b.marketing_relevance = true
    GROUP BY category_a, category_b
    HAVING co_occurrence >= 3
)
SELECT 
    category_a,
    category_b,
    co_occurrence,
    round(combined_interest, 2) as avg_combined_interest,
    multiIf(
        co_occurrence >= 10, 'STRONG_CORRELATION',
        co_occurrence >= 6, 'MODERATE_CORRELATION',
        'WEAK_CORRELATION'
    ) as correlation_strength
FROM category_pairs
ORDER BY co_occurrence DESC, combined_interest DESC;

-- 15. Trend Lifecycle Analysis
-- Analyze the lifecycle stages of trending topics
WITH trend_lifecycle AS (
    SELECT 
        topic,
        geo,
        toDate(crawled_at) as date,
        data_points,
        row_number() OVER (PARTITION BY topic, geo ORDER BY crawled_at) as day_sequence,
        max(data_points) OVER (PARTITION BY topic, geo) as peak_interest,
        min(data_points) OVER (PARTITION BY topic, geo) as min_interest
    FROM google_trends
    WHERE crawled_at >= now() - INTERVAL 7 DAY
      AND marketing_relevance = true
    GROUP BY topic, geo, date, data_points, crawled_at
),
lifecycle_stages AS (
    SELECT 
        topic,
        geo,
        date,
        data_points,
        peak_interest,
        day_sequence,
        CASE 
            WHEN data_points = peak_interest THEN 'PEAK'
            WHEN data_points >= peak_interest * 0.8 THEN 'MATURE'
            WHEN data_points >= peak_interest * 0.5 THEN 'GROWING'
            WHEN data_points >= peak_interest * 0.2 THEN 'EMERGING'
            ELSE 'DECLINING'
        END as lifecycle_stage
    FROM trend_lifecycle
)
SELECT 
    topic,
    count(DISTINCT geo) as geo_reach,
    max(peak_interest) as global_peak,
    groupArray(DISTINCT lifecycle_stage) as observed_stages,
    argMax(lifecycle_stage, date) as current_stage,
    datediff('day', min(date), max(date)) as trend_duration_days
FROM lifecycle_stages
GROUP BY topic
HAVING trend_duration_days >= 2  -- Multi-day trends only
ORDER BY global_peak DESC, geo_reach DESC;