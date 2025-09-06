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
                # Check if trend_events table exists and has data
                count_result = client.query("SELECT COUNT(*) as total FROM trend_events")
                print(f"Total rows in trend_events: {count_result.result_rows[0][0]}")
                
                # Check date range in trend_events
                date_check = client.query("SELECT MIN(timestamp) as min_date, MAX(timestamp) as max_date FROM trend_events")
                if date_check.result_rows:
                    print(f"Date range in trend_events: {date_check.result_rows[0][0]} to {date_check.result_rows[0][1]}")
                
                # Check available countries
                country_check = client.query("SELECT DISTINCT country_code FROM trend_events LIMIT 10")
                if country_check.result_rows:
                    print(f"Available countries: {[row[0] for row in country_check.result_rows]}")
                
                # Check available businesses
                business_check = client.query("SELECT DISTINCT business FROM trend_events LIMIT 10")
                if business_check.result_rows:
                    print(f"Available businesses: {[row[0] for row in business_check.result_rows]}")
                
                # Show sample data (denormalized - no JOINs needed)
                sample_result = client.query("SELECT topic_name, timestamp, stat_type, country_code, business FROM trend_events LIMIT 5")
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
        # Schema based on the updated trends_schema_and_queries.sql DDL file (denormalized)
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