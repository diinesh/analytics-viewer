from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import clickhouse_connect
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = None
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
    print("OpenAI client initialized successfully")
else:
    print("ERROR: OPENAI_API_KEY not found in environment")

# ClickHouse connection with detailed debugging
client = None
try:
    print("Attempting ClickHouse connection...")
    print(f"Host: {os.getenv('CLICKHOUSE_HOST')}")
    print(f"Port: {os.getenv('CLICKHOUSE_PORT')}")
    print(f"User: {os.getenv('CLICKHOUSE_USER')}")
    print(f"Database: {os.getenv('CLICKHOUSE_DATABASE')}")
    print(f"Secure: {os.getenv('CLICKHOUSE_SECURE')}")
    
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DATABASE", "default"),
        secure=os.getenv("CLICKHOUSE_SECURE", "false").lower() == "true"
    )
    
    # Test the connection
    test_result = client.query("SELECT 1 as test")
    print(f"ClickHouse connection successful! Test result: {test_result.result_rows}")
    
except Exception as e:
    print(f"ClickHouse connection failed: {type(e).__name__}: {str(e)}")
    import traceback
    print(f"Full traceback: {traceback.format_exc()}")
    client = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    sql: str
    data: List[Dict[str, Any]]
    chart_type: str
    title: str

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        print(f"Processing query: {request.query}")
        
        # Step 1: Convert to SQL
        print("Converting natural language to SQL...")
        sql_query = await convert_to_sql(request.query)
        print(f"Generated SQL: {sql_query}")
        
        # Step 2: Check ClickHouse connection
        if not client:
            print("ERROR: ClickHouse client not available")
            raise HTTPException(status_code=500, detail="ClickHouse connection not available")
        
        # Step 3: Execute query
        print("Executing query on ClickHouse...")
        result = client.query(sql_query)
        print(f"Query executed successfully, got {len(result.result_rows)} rows")
        
        # If no results, let's debug
        if len(result.result_rows) == 0:
            print("No results returned. Let's check table data...")
            try:
                # Check if table exists and has data
                count_result = client.query("SELECT COUNT(*) as total FROM google_trends")
                print(f"Total rows in google_trends: {count_result.result_rows[0][0]}")
                
                # Check date range
                date_check = client.query("SELECT MIN(trend_timestamp) as min_date, MAX(trend_timestamp) as max_date FROM google_trends WHERE trend_timestamp IS NOT NULL")
                if date_check.result_rows:
                    print(f"Date range in google_trends: {date_check.result_rows[0][0]} to {date_check.result_rows[0][1]}")
                
                # Show sample data
                sample_result = client.query("SELECT topic, trend_timestamp FROM google_trends LIMIT 5")
                print(f"Sample data: {sample_result.result_rows}")
                
            except Exception as debug_e:
                print(f"Debug query failed: {debug_e}")
        
        # Step 4: Process results
        data = []
        if result.result_rows:
            columns = result.column_names
            print(f"Columns: {columns}")
            for row in result.result_rows:
                data.append(dict(zip(columns, row)))
        
        # Step 5: Determine visualization
        chart_type = determine_chart_type(request.query, data)
        title = generate_title(request.query)
        print(f"Chart type: {chart_type}, Title: {title}")
        
        return QueryResponse(
            sql=sql_query,
            data=data,
            chart_type=chart_type,
            title=title
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in process_query: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {type(e).__name__}: {str(e)}")

async def convert_to_sql(natural_query: str) -> str:
    try:
        print("Getting schema information...")
        schema_info = await get_schema_info()
        
        prompt = f"""You are a ClickHouse SQL expert. Convert the natural language query to ClickHouse SQL using ONLY the tables and columns listed below.

CRITICAL RULES:
1. Use ONLY the table names and column names provided in the schema below
2. Do NOT create fictional table names like "marketing_trends" or "trending_topics"  
3. Use the actual table names: zero_shot_analysis, zero_shot_entities, zero_shot_trends, content_sources, google_trends, x_trending_topics
4. NEVER mix columns from different tables - check which table each column belongs to
5. Always include a LIMIT clause (typically LIMIT 100 unless specified otherwise)
6. Use proper ClickHouse syntax

COLUMN MAPPING BY TABLE:
zero_shot_analysis: id, content_hash, source_url, crawled_at, analyzed_at, content_title, content_text, content_length, specific_topic, broad_category, marketing_intent, confidence_score, business_contexts, trend_signals, model_name, processing_time_ms

google_trends: id, topic, geo, timeframe, category_id, category_name, search_type, trend_rank, interest_over_time, time_index, data_points, source, marketing_relevance, crawled_at, trend_timestamp

x_trending_topics: id, topic, hashtag, trend_rank, tweet_volume, location, virality_score, marketing_potential, brand_safety, social_category, target_demographics, marketing_actions, trending_at, crawled_at, analyzed_at

AVAILABLE SCHEMA:
{schema_info}

QUERY TO CONVERT: "{natural_query}"

Examples of CORRECT queries by table:

zero_shot_analysis queries:
- SELECT specific_topic, broad_category, confidence_score FROM zero_shot_analysis WHERE marketing_intent = 'high' LIMIT 20
- SELECT * FROM zero_shot_analysis WHERE analyzed_at >= now() - INTERVAL 7 DAY LIMIT 50

google_trends queries:  
- SELECT topic, geo, category_name, data_points FROM google_trends WHERE marketing_relevance = true LIMIT 15
- SELECT topic, trend_rank FROM google_trends WHERE trend_timestamp >= now() - INTERVAL 7 DAY ORDER BY trend_rank ASC LIMIT 20

x_trending_topics queries:
- SELECT topic, virality_score, marketing_potential FROM x_trending_topics ORDER BY virality_score DESC LIMIT 10
- SELECT hashtag, tweet_volume, brand_safety FROM x_trending_topics WHERE trending_at >= now() - INTERVAL 1 DAY LIMIT 25

WRONG examples (DO NOT DO):
- SELECT broad_category FROM google_trends (broad_category only exists in zero_shot_analysis)
- SELECT virality_score FROM google_trends (virality_score only exists in x_trending_topics)

IMPORTANT DATE/TIME RULES:
- Use "now() - INTERVAL X DAY" for time-based filtering (not toDate())
- DateTime columns: analyzed_at, crawled_at, trend_timestamp, trending_at, trend_detected_at
- Always use proper INTERVAL syntax: INTERVAL 1 DAY, INTERVAL 7 DAY, INTERVAL 1 HOUR

Return ONLY the SQL query, no explanations or markdown formatting."""
        
        print(prompt)
        
        print("Calling OpenAI API...")
        if not openai_client:
            raise Exception("OpenAI client not initialized - check API key")
            
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        sql = response.choices[0].message.content.strip()
        sql = re.sub(r'```sql\n?', '', sql)
        sql = re.sub(r'\n?```', '', sql)
        
        print(f"OpenAI returned SQL: {sql}")
        return sql
    except Exception as e:
        print(f"ERROR in convert_to_sql: {type(e).__name__}: {str(e)}")
        raise Exception(f"Error converting to SQL: {type(e).__name__}: {str(e)}")

async def get_schema_info() -> str:
    if not client:
        return "No schema available - ClickHouse not connected"
    
    try:
        # Define all tables and their descriptions for the complete analytics platform
        schema_info = """Available tables and their purpose:

Table: zero_shot_analysis
Purpose: Main analysis results from zero-shot topic classification
Key columns:
  - id (UUID): Unique identifier
  - content_hash (String): Hash of original content
  - source_url (String): URL source of content
  - crawled_at (DateTime): When content was crawled
  - analyzed_at (DateTime): When analysis was performed
  - content_title (String): Title of the content
  - content_text (String): Full text content
  - content_length (UInt32): Length of content
  - specific_topic (String): Identified specific topic
  - broad_category (LowCardinality(String)): General category
  - marketing_intent (LowCardinality(String)): Marketing intent classification
  - confidence_score (Float32): Analysis confidence (0-1)
  - business_contexts (Array(LowCardinality(String))): Business context tags
  - trend_signals (Array(String)): Trend indicators
  - model_name (String): ML model used
  - processing_time_ms (UInt32): Processing time

Table: zero_shot_entities
Purpose: Named entities extracted from analyzed content
Key columns:
  - analysis_id (UUID): Links to zero_shot_analysis
  - entity_name (String): Name of the entity
  - entity_type (LowCardinality(String)): Type of entity
  - confidence (Float32): Entity extraction confidence
  - relevance_score (Float32): Relevance to content
  - context_snippet (String): Context where entity appears

Table: zero_shot_trends  
Purpose: Trend analysis and momentum tracking
Key columns:
  - topic (String): Topic being tracked
  - trend_type (LowCardinality(String)): emerging/growing/stable/declining
  - momentum_score (Float32): Trend momentum indicator
  - mentions_count (UInt32): Number of mentions
  - trend_detected_at (DateTime): When trend was detected

Table: content_sources
Purpose: Tracking content sources and their crawling statistics
Key columns:
  - source_url (String): Source URL
  - domain (String): Domain name
  - source_type (LowCardinality(String)): website/reddit/twitter/etc
  - crawl_count (UInt32): Number of crawls
  - success_rate (Float32): Crawling success rate

Table: google_trends
Purpose: Google Trends data for trending topics and keyword search volumes
Key columns:
  - id (UUID): Unique identifier
  - topic (String): Trending topic or keyword
  - geo (LowCardinality(String)): Geographic location
  - timeframe (LowCardinality(String)): Time period
  - category_id (Int32): Google category ID
  - category_name (LowCardinality(String)): Category name
  - search_type (LowCardinality(String)): trending/keyword
  - trend_rank (UInt8): Ranking position
  - interest_over_time (String): JSON time series data
  - data_points (UInt16): Number of data points
  - marketing_relevance (Bool): Marketing relevance flag
  - crawled_at (DateTime): When data was collected
  - trend_timestamp (DateTime): When trend occurred

Table: google_trends_related
Purpose: Related queries from Google Trends
Key columns:
  - main_topic (String): Main trending topic
  - geo (LowCardinality(String)): Geographic location
  - related_query (String): Related search query
  - query_type (LowCardinality(String)): rising/top

Table: x_trending_topics
Purpose: X.com (Twitter) trending topics and social media analysis
Key columns:
  - id (UUID): Unique identifier
  - topic (String): Trending topic
  - hashtag (String): Associated hashtag
  - trend_rank (UInt8): Trend ranking
  - tweet_volume (UInt64): Number of tweets
  - location (LowCardinality(String)): Geographic location
  - virality_score (Float32): Virality measurement
  - marketing_potential (LowCardinality(String)): high/medium/low
  - brand_safety (LowCardinality(String)): safe/medium_risk/high_risk/unknown
  - social_category (LowCardinality(String)): Social media category
  - target_demographics (Array(String)): Target audience demographics
  - marketing_actions (Array(String)): Suggested marketing actions
  - trending_at (DateTime): When topic was trending
  - crawled_at (DateTime): When data was collected

Materialized Views (pre-aggregated data):
  - daily_analysis_stats: Daily aggregations of zero-shot analysis
  - google_trends_daily_summary: Daily Google Trends summaries
  - cross_source_topic_correlation: Cross-platform topic correlations
  - daily_trending_insights: Combined trending insights across all sources
  - x_trending_daily_summary: Daily X.com trending summaries

Common query patterns:
- Time-based analysis: Use analyzed_at, crawled_at, trending_at, trend_detected_at
- Topic analysis: Use specific_topic, topic, broad_category
- Confidence filtering: Use confidence_score >= 0.7 for high-confidence results
- Cross-platform analysis: Join zero_shot_analysis with google_trends or x_trending_topics on topic matching
- Marketing analysis: Filter by marketing_intent, marketing_potential, marketing_relevance
- Social media analysis: Use x_trending_topics for virality, brand safety, demographics
- Geographic analysis: Use geo column in google_trends and location in x_trending_topics
- Trend correlation: Use materialized views for pre-aggregated insights
"""
        
        return schema_info
    except Exception as e:
        return f"Error fetching schema: {str(e)}"

def determine_chart_type(query: str, data: List[Dict]) -> str:
    # Always return table for now - charts will be added later
    return "table"

def generate_title(query: str) -> str:
    return f"Results: {query[:50]}{'...' if len(query) > 50 else ''}"

@app.get("/api/health")
async def health_check():
    clickhouse_status = "disconnected"
    if client:
        try:
            # Test the connection
            result = client.query("SELECT 1")
            clickhouse_status = "connected"
        except Exception as e:
            clickhouse_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "clickhouse_connected": client is not None,
        "clickhouse_status": clickhouse_status,
        "openai_configured": openai_client is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)