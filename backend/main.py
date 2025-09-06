from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import clickhouse_connect
import os
from dotenv import load_dotenv
import json

from agents.sql.sql_agent import sql_agent
from agents.integrations.openai_client import openai_client
from agents.analysis.trending_agent import trending_analysis_agent

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client is now initialized in agents/integrations/openai_client.py

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

class TopicDetailResponse(BaseModel):
    topic_info: Dict[str, Any]
    time_series_data: List[Dict[str, Any]]
    stats: Dict[str, Any]

class TrendingAnalysisResponse(BaseModel):
    topic_info: Dict[str, Any]
    trending_analysis: Dict[str, Any]
    popularity_distribution: Dict[str, Any]
    content_summary: Dict[str, Any]
    web_context: Dict[str, Any]
    raw_data: Dict[str, Any]

class TrendingInsightsResponse(BaseModel):
    topic_name: str
    trend_score: float
    content_summary: str
    key_themes: List[str]
    geographic_focus: List[str]
    analysis_type: str

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        print(f"Processing query: {request.query}")
        
        # Step 1: Convert to SQL
        print("Converting natural language to SQL...")
        sql_query = await sql_agent.convert_to_sql(request.query)
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



def determine_chart_type(query: str, data: List[Dict]) -> str:
    # Always return table for now - charts will be added later
    return "table"

def generate_title(query: str) -> str:
    return f"Results: {query[:50]}{'...' if len(query) > 50 else ''}"

@app.get("/api/topic/{topic_id}", response_model=TopicDetailResponse)
async def get_topic_details(topic_id: int, time_range: str = "7d", stat_type: str = "all", country: str = "all"):
    try:
        print(f"Fetching details for topic ID: {topic_id}")
        
        if not client:
            raise HTTPException(status_code=500, detail="ClickHouse connection not available")
        
        # Build the natural language query for topic details using topic_id
        query = f'Show me detailed information about topic ID {topic_id}'
        
        time_mapping = {
            '1h': '1 HOUR',
            '6h': '6 HOUR', 
            '24h': '24 HOUR',
            '7d': '7 DAY',
            '30d': '30 DAY'
        }
        
        time_interval = time_mapping.get(time_range, '7 DAY')
        query += f' with time series data for the last {time_interval.lower()}'
        
        if stat_type != 'all':
            query += f' for {stat_type} statistics'
            
        if country != 'all':
            query += f' in {country}'
        
        print(f"Generated topic query: {query}")
        
        # Convert to SQL using agent
        sql_query = await sql_agent.generate_topic_detail_sql(topic_id, time_range, stat_type, country)
        print(f"Generated SQL for topic: {sql_query}")
        
        # Execute the query
        result = client.query(sql_query)
        
        # Process the results
        time_series_data = []
        topic_info = {}
        
        if result.result_rows:
            columns = result.column_names
            for row in result.result_rows:
                row_data = dict(zip(columns, row))
                time_series_data.append(row_data)
                
                # Extract topic info from first row
                if not topic_info:
                    topic_info = {
                        'topic_name': row_data.get('topic_name', f'Topic {topic_id}'),
                        'category': row_data.get('category'),
                        'business': row_data.get('business'),
                        'topic_id': row_data.get('topic_id', topic_id),
                        'trend_score': row_data.get('avg_trend_score') or row_data.get('trend_score')
                    }
        
        # Calculate stats
        stats = {}
        if time_series_data:
            trend_scores = [float(row.get('trend_score', 0) or row.get('avg_trend_score', 0)) for row in time_series_data if row.get('trend_score') or row.get('avg_trend_score')]
            stat_values = [float(row.get('stat_value', 0) or row.get('total_volume', 0)) for row in time_series_data if row.get('stat_value') or row.get('total_volume')]
            
            stats = {
                'total_events': len(time_series_data),
                'avg_trend_score': sum(trend_scores) / len(trend_scores) if trend_scores else 0,
                'peak_trend_score': max(trend_scores) if trend_scores else 0,
                'total_volume': sum(stat_values) if stat_values else 0,
                'countries': list(set([row.get('country_code') for row in time_series_data if row.get('country_code')])),
                'stat_types': list(set([row.get('stat_type') for row in time_series_data if row.get('stat_type')])),
                'date_range': {
                    'start': min([row.get('timestamp') for row in time_series_data if row.get('timestamp')], default=''),
                    'end': max([row.get('timestamp') for row in time_series_data if row.get('timestamp')], default='')
                }
            }
        
        # If no topic info was found, create a basic one
        if not topic_info:
            topic_info = {
                'topic_name': f'Topic {topic_id}',
                'category': None,
                'business': None,
                'topic_id': topic_id,
                'trend_score': None
            }
        
        return TopicDetailResponse(
            topic_info=topic_info,
            time_series_data=time_series_data,
            stats=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_topic_details: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {type(e).__name__}: {str(e)}")

@app.get("/api/topic/{topic_id}/analysis", response_model=TrendingAnalysisResponse)
async def get_topic_analysis(topic_id: int, time_range: str = "24h"):
    """
    Get comprehensive trending analysis for a specific topic
    """
    try:
        print(f"Getting trending analysis for topic ID: {topic_id}")
        
        # Get comprehensive analysis from trending agent
        analysis = await trending_analysis_agent.analyze_topic_trending(topic_id, time_range)
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        
        return TrendingAnalysisResponse(**analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_topic_analysis: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {type(e).__name__}: {str(e)}")

@app.get("/api/topic/{topic_id}/insights", response_model=TrendingInsightsResponse)
async def get_topic_insights(topic_id: int, time_range: str = "24h"):
    """
    Get quick trending insights summary for a specific topic
    """
    try:
        print(f"Getting trending insights for topic ID: {topic_id}")
        
        # Get quick insights summary
        insights = await trending_analysis_agent.get_trending_insights_summary(topic_id, time_range)
        
        if "error" in insights:
            raise HTTPException(status_code=500, detail=insights["error"])
        
        return TrendingInsightsResponse(**insights)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_topic_insights: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Insights failed: {type(e).__name__}: {str(e)}")

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
        "openai_configured": openai_client.is_available()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)