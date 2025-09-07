"""
Analysis prompts for trending topic insights and content analysis
"""

def get_trending_analysis_prompt(topic_data: dict, web_context: dict) -> tuple[str, str]:
    """
    Generate system and user prompts for comprehensive trending analysis
    
    Args:
        topic_data: Database trending data (trend_score, category, etc.)
        web_context: Web search results and content summary
        
    Returns:
        Tuple of (system_message, user_message)
    """
    
    system_message = """You are an expert trending topics analyst with deep knowledge of social media trends, news cycles, and digital content patterns. 

Your role is to:
- Analyze trending data objectively and factually
- Identify the core reasons behind trending patterns
- Predict trend trajectories based on historical patterns
- Provide actionable insights for content strategists and marketers

Always respond in valid JSON format. Base your analysis on the provided data and clearly indicate when information is limited or unavailable."""

    user_message = f"""Analyze why this topic is trending and provide comprehensive insights.

TOPIC TRENDING DATA:
- Topic Name: {topic_data.get('topic_name', 'Unknown')}
- Category: {topic_data.get('category', 'Unknown')}
- Business Vertical: {topic_data.get('business', 'Unknown')}
- Current Trend Score: {topic_data.get('avg_trend_score', 0)}/100
- Peak Trend Score: {topic_data.get('peak_trend_score', 0)}/100
- Total Volume: {topic_data.get('total_volume', 0):,} interactions
- Geographic Focus: {topic_data.get('top_regions', [])}
- Active Countries: {topic_data.get('countries', [])}
- Stat Types: {topic_data.get('stat_types', [])}
- Time Range: {topic_data.get('time_range', '24h')}

WEB CONTENT CONTEXT:
Search Query Used: {web_context.get('search_query', 'N/A')}
Content Summary: {web_context.get('content_summary', 'No web context available')}
Key Themes: {web_context.get('key_themes', [])}

Provide your analysis in this exact JSON structure:

{{
    "trending_reason": {{
        "primary_cause": "Main reason this topic is trending (1-2 sentences)",
        "specific_event": "Specific event/content driving the trend",
        "timing_factor": "Why it's trending NOW (timing relevance)"
    }},
    "content_analysis": {{
        "content_type": "Type of content (news, sports event, announcement, etc.)",
        "story_summary": "Brief story summary (2-3 sentences)",
        "key_drivers": ["List", "of", "content", "drivers"],
        "viral_factors": ["Why", "this", "content", "spreads"]
    }},
    "trend_patterns": {{
        "velocity": "Trend growth pattern (rapid/steady/declining)",
        "momentum": "Current momentum (accelerating/stable/slowing)",
        "geographic_insight": "Why trending in specific regions",
        "demographic_appeal": "Who this appeals to and why"
    }},
    "business_context": {{
        "category_fit": "Why this fits the category classification",
        "business_relevance": "Relevance to the business vertical",
        "market_impact": "Potential business/market implications"
    }},
    "prediction": {{
        "trend_duration": "How long this will likely trend",
        "peak_prediction": "If/when it will peak",
        "related_trends": "Other topics likely to trend as a result"
    }}
}}"""

    return system_message, user_message


def get_popularity_distribution_prompt(distribution_data: dict) -> tuple[str, str]:
    """
    Generate system and user prompts for analyzing popularity distribution across categories/businesses
    """
    
    system_message = """You are a data analyst specializing in trend distribution patterns and audience segmentation.

Your expertise covers:
- Cross-category trend analysis and audience overlap
- Geographic and demographic trend distribution
- Business vertical impact assessment
- Engagement pattern recognition across different segments
- Cultural and regional factors affecting content popularity

Always respond in valid JSON format. Provide data-driven insights based on the distribution metrics provided."""

    user_message = f"""Analyze the popularity distribution of this trending topic across different dimensions.

DISTRIBUTION DATA:
Category Breakdown: {distribution_data.get('category_breakdown', {})}
Business Breakdown: {distribution_data.get('business_breakdown', {})}
Geographic Distribution: {distribution_data.get('geographic_breakdown', {})}
Stat Type Distribution: {distribution_data.get('stat_type_breakdown', {})}

Provide your analysis in this exact JSON structure:

{{
    "category_analysis": {{
        "dominant_category": "Primary category with explanation",
        "cross_category_appeal": "Why it appeals across categories",
        "category_insights": "Key insights about category distribution"
    }},
    "business_analysis": {{
        "primary_business": "Main business vertical",
        "business_crossover": "How it crosses business boundaries", 
        "commercial_potential": "Business/commercial implications"
    }},
    "geographic_analysis": {{
        "geographic_concentration": "Where it's most popular and why",
        "regional_variations": "How popularity varies by region",
        "cultural_factors": "Cultural factors affecting distribution"
    }},
    "engagement_analysis": {{
        "engagement_types": "What types of engagement are driving this",
        "audience_behavior": "How different audiences engage",
        "growth_patterns": "How engagement is growing/changing"
    }}
}}"""

    return system_message, user_message


def get_content_summary_prompt(topic_name: str, web_content: str, category: str) -> tuple[str, str]:
    """
    Generate system and user prompts for creating topic content summary
    """
    
    system_message = """You are a content analyst specializing in trending topics and digital content summarization.

Your expertise includes:
- Extracting key insights from web content and news articles
- Identifying stakeholders and affected parties
- Understanding content themes and emotional tones
- Providing contextual background and historical perspective
- Predicting content trajectory and future developments

Always respond in valid JSON format. Be factual and objective. When information is limited or unavailable, clearly state this in your response."""

    user_message = f"""Create a comprehensive content summary for this trending topic.

TOPIC: {topic_name}
CATEGORY: {category}
WEB CONTENT: {web_content}

Provide your summary in this exact JSON structure:

{{
    "topic_overview": {{
        "what_it_is": "Clear description of what this topic represents",
        "why_notable": "Why this topic is notable/newsworthy",
        "context": "Important context/background information"
    }},
    "content_themes": {{
        "primary_themes": ["Main", "content", "themes"],
        "secondary_themes": ["Supporting", "themes"],
        "emotional_tone": "Overall emotional tone of content"
    }},
    "stakeholders": {{
        "key_people": ["Important", "people", "involved"],
        "organizations": ["Companies", "teams", "organizations"],
        "affected_parties": ["Who", "is", "impacted"]
    }},
    "timeline": {{
        "key_events": "Chronology of important events",
        "current_status": "Current situation/status",
        "what_next": "What might happen next"
    }},
    "significance": {{
        "immediate_impact": "Immediate effects/impact",
        "broader_implications": "Wider implications/consequences",
        "historical_context": "How this fits into broader context"
    }}
}}"""

    return system_message, user_message


def get_trend_comparison_prompt(current_data: dict, historical_data: dict) -> tuple[str, str]:
    """
    Generate system and user prompts for comparing current trends with historical patterns
    """
    
    system_message = """You are a trend forecasting specialist with expertise in historical pattern analysis and predictive modeling.

Your core competencies include:
- Comparative analysis of trending patterns across different time periods
- Recognition of cyclical and seasonal trending behaviors
- Velocity and momentum analysis for trend trajectories
- Pattern matching with similar historical events
- Predictive modeling based on historical precedents

Always respond in valid JSON format. Base predictions on observable patterns in the historical data and clearly indicate confidence levels where appropriate."""

    user_message = f"""Compare current trending patterns with historical data to identify insights and predictions.

CURRENT TRENDING DATA:
{current_data}

HISTORICAL COMPARISON DATA:
{historical_data}

Provide your comparative analysis in this exact JSON structure:

{{
    "trend_velocity": {{
        "current_vs_historical": "How current velocity compares",
        "acceleration_pattern": "Pattern of growth/decline",
        "unusual_patterns": "Any unusual or noteworthy patterns"
    }},
    "volume_analysis": {{
        "volume_comparison": "How current volume compares to past",
        "peak_analysis": "Peak performance vs historical peaks",
        "sustainability": "Likely sustainability of current trend"
    }},
    "pattern_recognition": {{
        "similar_events": "Similar historical trending events",
        "pattern_type": "Type of trending pattern this represents",
        "cycle_analysis": "Where this fits in trending cycles"
    }},
    "predictive_insights": {{
        "trajectory_prediction": "Predicted trajectory based on patterns",
        "duration_estimate": "Estimated duration based on similar trends",
        "intensity_forecast": "Predicted intensity changes"
    }}
}}"""

    return system_message, user_message