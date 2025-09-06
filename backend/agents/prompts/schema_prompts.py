"""
Schema information prompts and templates
"""

def get_schema_info() -> str:
    """
    Get the database schema information for trending data
    
    Returns:
        Formatted schema information for use in prompts
    """
    schema_info = """Available tables and their purpose:

Table: trend_events (DENORMALIZED STRUCTURE)
Purpose: Time-series events with denormalized topic information and geographic hierarchy
Key columns:
  - event_id (UInt64): Unique event identifier (PRIMARY KEY)
  - topic_id (UInt32): Topic identifier
  - topic_name (LowCardinality(String)): Denormalized topic name
  - category (LowCardinality(String)): Denormalized topic category
  - business (LowCardinality(String)): Denormalized business vertical/industry
  - timestamp (DateTime64(3)): Event timestamp with millisecond precision
  - country_code (LowCardinality(String)): Country code ('US', 'CA', 'GB', etc.)
  - region_code (LowCardinality(String)): State/province code ('TX', 'NY', 'ON', 'BC', etc.)
  - city_code (LowCardinality(String)): City code ('NYC', 'LAX', 'TOR', etc.)
  - stat_type (LowCardinality(String)): Type of statistic ('appearance', 'search_volume', 'mentions', etc.)
  - stat_value (Float64): The actual statistic value
  - trend_score (Float32): Overall trend strength/momentum at this point
  - date (Date): Materialized date field partitioned by YYYYMM

Storage and Performance:
- Partitioned by month: PARTITION BY toYYYYMM(date)
- Optimized for time-series and geographic queries: ORDER BY (timestamp, country_code, topic_id)
- Denormalized structure eliminates need for JOINs
- Geographic hierarchy: country_code -> region_code -> city_code

Common query patterns:
- Time-based trending analysis: Filter by timestamp with INTERVAL queries
- Geographic analysis: Filter by country_code, region_code, or city_code
- Business/category analysis: Filter by business or category (no JOINs needed)
- Stat type analysis: Filter by stat_type (search_volume, mentions, etc.)
- Recent trends: Use timestamp >= now() - INTERVAL X HOUR/DAY/MINUTE
- Multi-country analysis: Use country_code IN ('US', 'CA') for regional comparisons
"""
    
    return schema_info