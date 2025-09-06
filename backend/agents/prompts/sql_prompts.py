"""
SQL generation prompts for different types of queries
"""

def get_sql_generation_prompt(natural_query: str, schema_info: str) -> str:
    """
    Generate the main SQL conversion prompt
    
    Args:
        natural_query: The user's natural language query
        schema_info: Database schema information
        
    Returns:
        Complete prompt for OpenAI API
    """
    return f"""You are a ClickHouse SQL expert. Convert the natural language query to ClickHouse SQL using ONLY the tables and columns listed below.

CRITICAL RULES:
1. Use ONLY the table names and column names provided in the schema below
2. The main table is: trend_events (DENORMALIZED - no JOINs needed!)
3. All topic information is already denormalized in trend_events table
4. NEVER use JOINs - all data is in the single trend_events table
5. Always include a LIMIT clause (typically LIMIT 50 unless specified otherwise)
6. Use proper ClickHouse syntax

COLUMN MAPPING FOR trend_events:
event_id, topic_id, topic_name, category, business, timestamp, country_code, region_code, city_code, stat_type, stat_value, trend_score, date

AVAILABLE SCHEMA:
{schema_info}

QUERY TO CONVERT: "{natural_query}"

Examples of CORRECT queries using the denormalized schema:

Basic trending topics (last 24 hours):
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

Recent trending (last 15 minutes):
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

Trending by business:
SELECT 
    topic_name,
    business,
    avg(trend_score) as trend_score,
    sum(stat_value) as total_volume
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
  AND business = 'tech'
GROUP BY topic_id, topic_name, business
ORDER BY trend_score DESC
LIMIT 25;

Trending by category:
SELECT 
    topic_name,
    category,
    avg(trend_score) as trend_score,
    sum(stat_value) as total_volume
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
  AND category = 'sports'
GROUP BY topic_id, topic_name, category
ORDER BY trend_score DESC
LIMIT 25;

Trending by stat type:
SELECT 
    topic_name,
    stat_type,
    avg(trend_score) as avg_trend_score,
    sum(stat_value) as total_stat_value
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
  AND stat_type = 'search_volume'
GROUP BY topic_id, topic_name, stat_type
ORDER BY avg_trend_score DESC
LIMIT 20;

Trending by Country:
SELECT 
    topic_name,
    country_code,
    avg(trend_score) as avg_trend_score
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
  AND country_code = 'US'
GROUP BY topic_id, topic_name, country_code
ORDER BY avg_trend_score DESC
LIMIT 20;

Trending by State/Region:
SELECT 
    topic_name,
    country_code,
    region_code,
    avg(trend_score) as avg_trend_score
FROM trend_events
WHERE timestamp >= now() - INTERVAL 24 HOUR
  AND country_code = 'US'
  AND region_code = 'CA'
GROUP BY topic_id, topic_name, country_code, region_code
ORDER BY avg_trend_score DESC
LIMIT 20;

Multi-country analysis (US and Canada):
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

IMPORTANT RULES:
- NO JOINs needed - all data is denormalized in trend_events table
- Use "now() - INTERVAL X DAY/HOUR/MINUTE" for time-based filtering
- DateTime column: timestamp
- Geographic filtering: country_code, region_code, city_code
- Always use proper INTERVAL syntax: INTERVAL 1 DAY, INTERVAL 6 HOUR, INTERVAL 15 MINUTE

Return ONLY the SQL query, no explanations or markdown formatting."""


def get_topic_detail_prompt(topic_id: int, time_range: str, stat_type: str, country: str, schema_info: str) -> str:
    """
    Generate prompt for topic detail queries
    
    Args:
        topic_id: ID of the topic to analyze
        time_range: Time range for the analysis
        stat_type: Type of statistics to analyze
        country: Country filter
        schema_info: Database schema information
        
    Returns:
        Complete prompt for topic detail analysis
    """
    time_mapping = {
        '1h': '1 HOUR',
        '6h': '6 HOUR', 
        '24h': '24 HOUR',
        '7d': '7 DAY',
        '30d': '30 DAY'
    }
    
    time_interval = time_mapping.get(time_range, '7 DAY')
    query = f'Show me detailed information about topic ID {topic_id} with time series data for the last {time_interval.lower()}'
    
    if stat_type != 'all':
        query += f' for {stat_type} statistics'
        
    if country != 'all':
        query += f' in {country}'
    
    return get_sql_generation_prompt(query, schema_info)