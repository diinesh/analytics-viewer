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
from agents.marketing.campaign_generator import campaign_generator
from agents.marketing.models import BrandProfile, AudienceProfile, CampaignRequest

load_dotenv()

app = FastAPI(
    title="Analytics Viewer API",
    description="""
    🚀 **Analytics Viewer API** - AI-Powered Trending Topics Analysis & Marketing Campaign Generator
    
    ## Features
    
    ### 📊 **Analytics & Querying**
    * Natural language to SQL conversion
    * ClickHouse database integration  
    * Real-time trending analysis
    
    ### 📈 **Trending Analysis**
    * Topic trending analysis with AI insights
    * Web context integration
    * Performance predictions
    
    ### 🎯 **Marketing Campaign Generation**
    * AI-powered campaign strategy
    * Multi-channel content generation (LinkedIn, Twitter, Instagram, Email)
    * Brand and audience profiling
    * ROI and performance predictions
    
    ## Getting Started
    
    1. **Query Data**: Use `/api/query` to ask questions in natural language
    2. **Analyze Topics**: Get trending insights with `/api/topics/{topic_id}/analysis`  
    3. **Generate Campaigns**: Create marketing campaigns with `/api/campaigns/generate`
    
    ## Support
    
    * GitHub: [analytics-viewer](https://github.com/your-org/analytics-viewer)
    * Documentation: [docs](https://your-docs.com)
    """,
    version="1.0.0",
    contact={
        "name": "Analytics Viewer Team",
        "url": "https://your-website.com",
        "email": "support@your-website.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Query & Analytics",
            "description": "Natural language queries and data analysis endpoints"
        },
        {
            "name": "Trending Analysis", 
            "description": "AI-powered trending topic analysis and insights"
        },
        {
            "name": "Marketing Campaigns",
            "description": "Marketing campaign generation and management"
        },
        {
            "name": "Health & Status",
            "description": "API health checks and system status"
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://analytics-frontend-simple-sqljbnaquq-uc.a.run.app"
    ],
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

# Marketing Campaign Models
class BrandProfileRequest(BaseModel):
    brand_name: str
    industry: str
    business_vertical: str
    brand_voice: str  # "professional", "casual", "witty", "authoritative"
    target_markets: List[str]
    core_values: List[str]
    prohibited_topics: List[str] = []
    website_url: str = None
    logo_url: str = None

class AudienceProfileRequest(BaseModel):
    demographics: Dict[str, Any]
    interests: List[str]
    pain_points: List[str]
    preferred_platforms: List[str]
    content_preferences: List[str]
    geographic_focus: List[str]
    age_range: str = None
    income_level: str = None

class CampaignGenerationRequest(BaseModel):
    topic_id: int
    brand_profile: BrandProfileRequest
    audience_profile: AudienceProfileRequest
    campaign_goals: List[str]
    channels: List[str]
    budget: float = None
    duration_days: int = 7
    urgent: bool = False

class CampaignResponse(BaseModel):
    campaign_id: str
    campaign_brief: Dict[str, Any]
    campaign_content: Dict[str, Any]
    content_calendar: Dict[str, Any]
    performance_predictions: Dict[str, Any]
    budget_breakdown: Dict[str, Any]
    generated_at: str

@app.post(
    "/api/query", 
    response_model=QueryResponse,
    tags=["Query & Analytics"],
    summary="🔍 Process Natural Language Query",
    description="""
    Convert natural language questions into SQL queries and execute them against ClickHouse.
    
    **Example queries:**
    * "Show me trending topics in the last 24 hours"
    * "What are the top 10 topics by search volume?"
    * "Find topics trending in the US with high engagement"
    
    The system automatically:
    1. Converts your question to optimized ClickHouse SQL
    2. Executes the query safely
    3. Returns structured results with visualization hints
    """,
    response_description="Query results with SQL, data, and chart type suggestions"
)
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

@app.get(
    "/api/topic/{topic_id}/analysis", 
    response_model=TrendingAnalysisResponse,
    tags=["Trending Analysis"],
    summary="📈 Get Comprehensive Topic Analysis",
    description="""
    Get detailed AI-powered analysis of why a specific topic is trending.
    
    **Features:**
    * **Trending Reasons** - Why the topic is gaining attention
    * **Content Analysis** - What type of content is driving engagement  
    * **Business Context** - Relevant business implications and opportunities
    * **Geographic Insights** - Where the trend is strongest
    * **Performance Predictions** - Expected trend trajectory
    
    **Time Range Options:**
    * `1h` - Last hour (real-time analysis)
    * `24h` - Last 24 hours (default)
    * `7d` - Last 7 days (weekly trends)
    * `30d` - Last 30 days (monthly trends)
    """,
    response_description="Comprehensive trending analysis with AI insights and predictions"
)
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

@app.post(
    "/api/campaigns/generate", 
    response_model=CampaignResponse,
    tags=["Marketing Campaigns"],
    summary="🚀 Generate AI-Powered Marketing Campaign",
    description="""
    Generate a comprehensive, multi-channel marketing campaign based on trending topics.
    
    **🎯 Campaign Generation Process:**
    1. **Trending Analysis** - Analyzes why the topic is trending
    2. **Strategy Development** - Creates brand-aligned campaign strategy  
    3. **Multi-Channel Content** - Generates platform-specific content:
       - **LinkedIn** - Professional B2B posts with thought leadership
       - **Twitter** - Viral engagement posts with trending hashtags  
       - **Instagram** - Visual content with aesthetic appeal
       - **Email** - Nurture sequences with high conversion rates
    4. **Performance Predictions** - ROI estimates and success metrics
    5. **Content Calendar** - Optimal posting schedule and timing
    
    **✨ AI-Powered Features:**
    * Brand voice consistency across all platforms
    * Audience-specific messaging and tone
    * Trending hashtags and optimal timing
    * Visual content suggestions  
    * A/B testing recommendations
    * Budget allocation optimization
    
    **📊 Expected Results:**
    * 5-8 social media posts per platform
    * 3-email nurture sequence
    * Content calendar with optimal timing
    * Performance predictions and ROI estimates
    * Budget breakdown and allocation strategy
    """,
    response_description="Complete marketing campaign with multi-channel content, strategy, and performance predictions"
)
async def generate_marketing_campaign(request: CampaignGenerationRequest):
    """
    Generate a complete marketing campaign from a trending topic
    """
    try:
        print(f"Generating marketing campaign for topic ID: {request.topic_id}")
        
        # Convert Pydantic models to dataclass models
        brand_profile = BrandProfile(
            brand_name=request.brand_profile.brand_name,
            industry=request.brand_profile.industry,
            business_vertical=request.brand_profile.business_vertical,
            brand_voice=request.brand_profile.brand_voice,
            target_markets=request.brand_profile.target_markets,
            core_values=request.brand_profile.core_values,
            prohibited_topics=request.brand_profile.prohibited_topics,
            website_url=request.brand_profile.website_url,
            logo_url=request.brand_profile.logo_url
        )
        
        audience_profile = AudienceProfile(
            demographics=request.audience_profile.demographics,
            interests=request.audience_profile.interests,
            pain_points=request.audience_profile.pain_points,
            preferred_platforms=request.audience_profile.preferred_platforms,
            content_preferences=request.audience_profile.content_preferences,
            geographic_focus=request.audience_profile.geographic_focus,
            age_range=request.audience_profile.age_range,
            income_level=request.audience_profile.income_level
        )
        
        campaign_request = CampaignRequest(
            topic_id=request.topic_id,
            brand_profile=brand_profile,
            audience_profile=audience_profile,
            campaign_goals=request.campaign_goals,
            channels=request.channels,
            budget=request.budget,
            duration_days=request.duration_days,
            urgent=request.urgent
        )
        
        # Generate the complete campaign
        campaign = await campaign_generator.generate_complete_campaign(campaign_request)
        
        if "error" in campaign:
            raise HTTPException(status_code=500, detail=campaign["error"])
        
        return CampaignResponse(**campaign)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in generate_marketing_campaign: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Campaign generation failed: {type(e).__name__}: {str(e)}")

@app.get(
    "/api/campaigns/examples",
    tags=["Marketing Campaigns"],
    summary="📋 Get Campaign Templates & Examples",
    description="""
    Get pre-built brand profiles, audience templates, and campaign configuration options.
    
    **🏢 Brand Profile Templates:**
    * **Tech Startup** - SaaS, authoritative voice, B2B focus
    * **Fashion E-commerce** - Trendy, Gen Z/Millennial focus
    * **Healthcare** - Professional, trust-focused, compliance-aware
    * **Financial Services** - Authoritative, security-focused, B2B/B2C
    
    **👥 Audience Profile Templates:**  
    * **B2B Professionals** - Decision makers, productivity-focused
    * **Gen Z Consumers** - Social-first, authenticity-focused
    * **Enterprise Buyers** - ROI-focused, process-driven
    * **Small Business Owners** - Efficiency and growth-focused
    
    **⚙️ Configuration Options:**
    * **Campaign Goals** - Brand awareness, lead gen, engagement, sales
    * **Channels** - LinkedIn, Twitter, Instagram, TikTok, Email, Blog
    * **Budget Ranges** - From startup ($1K) to enterprise ($100K+)
    * **Duration Options** - Sprint (7d) to long-term (90d)
    
    Perfect for quick campaign setup and understanding available options.
    """,
    response_description="Brand templates, audience profiles, and configuration options for campaign generation"
)
async def get_campaign_examples():
    """
    Get example brand profiles and audience profiles for testing
    """
    return {
        "brand_examples": [
            {
                "name": "Tech Startup",
                "profile": {
                    "brand_name": "AIFlow",
                    "industry": "SaaS",
                    "business_vertical": "tech",
                    "brand_voice": "authoritative",
                    "target_markets": ["B2B", "Enterprise"],
                    "core_values": ["Innovation", "Efficiency", "Trust"],
                    "prohibited_topics": ["Politics", "Religion"],
                    "website_url": "https://aiflow.com",
                    "logo_url": None
                }
            },
            {
                "name": "Fashion E-commerce",
                "profile": {
                    "brand_name": "RetroVibes",
                    "industry": "Fashion",
                    "business_vertical": "retail",
                    "brand_voice": "trendy",
                    "target_markets": ["Gen Z", "Millennials"],
                    "core_values": ["Self-expression", "Sustainability", "Inclusivity"],
                    "prohibited_topics": ["Fast fashion criticism"],
                    "website_url": "https://retrovibes.com",
                    "logo_url": None
                }
            }
        ],
        "audience_examples": [
            {
                "name": "B2B Professionals",
                "profile": {
                    "demographics": {"age_range": "25-45", "income": "75k-150k", "education": "Bachelor+"},
                    "interests": ["Productivity", "AI", "Business Growth", "Technology"],
                    "pain_points": ["Time management", "Tool fragmentation", "ROI measurement"],
                    "preferred_platforms": ["linkedin", "twitter", "email"],
                    "content_preferences": ["Educational", "Data-driven", "Case studies"],
                    "geographic_focus": ["US", "CA", "UK"],
                    "age_range": "25-45",
                    "income_level": "75k-150k"
                }
            },
            {
                "name": "Fashion-Forward Gen Z",
                "profile": {
                    "demographics": {"age_range": "18-25", "income": "25k-50k", "education": "High School+"},
                    "interests": ["Fashion", "Sustainability", "Social causes", "Self-expression"],
                    "pain_points": ["Budget constraints", "Finding authentic brands", "Size inclusivity"],
                    "preferred_platforms": ["instagram", "tiktok", "email"],
                    "content_preferences": ["Visual", "Authentic", "Behind-the-scenes"],
                    "geographic_focus": ["US", "CA", "UK", "AU"],
                    "age_range": "18-25",
                    "income_level": "25k-50k"
                }
            }
        ],
        "campaign_goals": [
            "brand_awareness",
            "lead_generation", 
            "engagement",
            "sales",
            "thought_leadership"
        ],
        "channels": [
            "linkedin",
            "twitter", 
            "instagram",
            "tiktok",
            "facebook",
            "email",
            "blog"
        ]
    }

@app.get(
    "/api/health",
    tags=["Health & Status"],
    summary="🏥 API Health Check",
    description="""
    Check the health and status of the Analytics Viewer API and its dependencies.
    
    **System Status:**
    * **API Server** - FastAPI application status
    * **ClickHouse** - Database connectivity and query performance  
    * **OpenAI** - AI service availability for analysis and campaign generation
    * **Web Search** - Google Custom Search API status for trending context
    
    **Response Codes:**
    * `200` - All systems operational
    * `503` - Service degraded (some dependencies unavailable)
    * `500` - Critical system failure
    
    Use this endpoint for monitoring, alerting, and debugging connectivity issues.
    """,
    response_description="Health status of API and all integrated services"
)
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