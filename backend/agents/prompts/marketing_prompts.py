"""
Marketing campaign generation prompts
"""
from typing import Dict, Any, Tuple


def get_campaign_strategy_prompt(trending_analysis: Dict[str, Any], brand_profile: Dict[str, Any], audience_profile: Dict[str, Any]) -> Tuple[str, str]:
    """Generate system and user prompts for campaign strategy creation"""
    
    system_message = """You are a digital marketing strategist specializing in trend-based campaigns and multi-channel marketing.

Your expertise includes:
- Converting trending topics into authentic brand campaigns
- Multi-channel campaign development and optimization
- Audience-specific messaging and content strategies
- Performance prediction and success metrics definition
- Brand-trend alignment without compromising authenticity
- Content calendar planning and timing optimization

Always respond in valid JSON format. Create campaigns that authentically connect trending topics to brand objectives while respecting brand values and audience preferences."""

    user_message = f"""Create a comprehensive marketing campaign strategy for this trending topic:

TRENDING ANALYSIS:
Topic: {trending_analysis.get('topic_info', {}).get('topic_name', 'Unknown')}
Trending Reason: {trending_analysis.get('trending_analysis', {}).get('trending_reason', {})}
Content Analysis: {trending_analysis.get('trending_analysis', {}).get('content_analysis', {})}
Business Context: {trending_analysis.get('trending_analysis', {}).get('business_context', {})}
Predictions: {trending_analysis.get('trending_analysis', {}).get('prediction', {})}
Geographic Focus: {trending_analysis.get('trending_analysis', {}).get('trend_patterns', {}).get('geographic_insight', 'Global')}

BRAND PROFILE:
Brand: {brand_profile.get('brand_name', 'Unknown')}
Industry: {brand_profile.get('industry', 'Unknown')}
Business Vertical: {brand_profile.get('business_vertical', 'Unknown')}
Brand Voice: {brand_profile.get('brand_voice', 'professional')}
Core Values: {brand_profile.get('core_values', [])}
Target Markets: {brand_profile.get('target_markets', [])}
Prohibited Topics: {brand_profile.get('prohibited_topics', [])}

AUDIENCE PROFILE:
Demographics: {audience_profile.get('demographics', {})}
Interests: {audience_profile.get('interests', [])}
Pain Points: {audience_profile.get('pain_points', [])}
Preferred Platforms: {audience_profile.get('preferred_platforms', [])}
Content Preferences: {audience_profile.get('content_preferences', [])}
Geographic Focus: {audience_profile.get('geographic_focus', [])}

Generate a comprehensive campaign strategy in this exact JSON structure:

{{
    "campaign_concept": {{
        "theme": "Central campaign theme connecting trend to brand",
        "key_message": "Primary message across all channels",
        "brand_angle": "How this trend relates specifically to our brand",
        "call_to_action": "Primary CTA across campaign",
        "campaign_duration": "recommended campaign duration",
        "urgency_level": "high/medium/low based on trend momentum"
    }},
    "channel_strategy": {{
        "social_media": {{
            "recommended_platforms": ["list of platforms"],
            "content_types": ["post types per platform"],
            "posting_frequency": "posts per day/week",
            "optimal_timing": "best posting times",
            "engagement_tactics": ["specific engagement strategies"]
        }},
        "email": {{
            "sequence_type": "nurture/promotional/educational",
            "email_count": "number of emails in sequence",
            "send_schedule": "timing between emails",
            "segmentation": "audience segmentation strategy",
            "personalization": "personalization approach"
        }},
        "content_marketing": {{
            "blog_topics": ["suggested blog post topics"],
            "video_concepts": ["video content ideas"],
            "infographic_ideas": ["visual content suggestions"]
        }}
    }},
    "content_pillars": {{
        "educational": "educational content angle and topics",
        "promotional": "promotional content approach", 
        "engagement": "engagement-focused content strategy",
        "social_proof": "social proof and credibility content",
        "trending_participation": "how to participate in the trend authentically"
    }},
    "success_metrics": {{
        "awareness_kpis": ["brand awareness metrics to track"],
        "engagement_kpis": ["engagement metrics to measure"],
        "conversion_kpis": ["conversion and lead metrics"],
        "brand_sentiment": "brand sentiment tracking approach"
    }},
    "risk_assessment": {{
        "brand_safety_score": "1-10 score for brand safety",
        "potential_risks": ["list of potential risks"],
        "mitigation_strategies": ["risk mitigation approaches"],
        "monitoring_requirements": ["what to monitor during campaign"]
    }},
    "budget_allocation": {{
        "content_creation": "% for content creation",
        "paid_promotion": "% for paid advertising",
        "influencer_collaboration": "% for influencer partnerships",
        "tools_and_analytics": "% for tools and measurement"
    }}
}}"""

    return system_message, user_message


def get_social_media_content_prompt(campaign_brief: Dict[str, Any], platform: str, post_count: int) -> Tuple[str, str]:
    """Generate system and user prompts for social media content creation"""
    
    platform_contexts = {
        "linkedin": "professional networking and B2B engagement with thought leadership focus",
        "twitter": "real-time conversations and viral engagement with concise messaging",
        "instagram": "visual storytelling and lifestyle content with strong aesthetic appeal",
        "tiktok": "entertainment and trend participation with creative video concepts",
        "facebook": "community building and longer-form content with diverse demographics"
    }
    
    system_message = f"""You are a {platform.title()} content strategist expert in creating viral, engaging content that drives business results.

Your expertise includes:
- Platform-specific content optimization and best practices
- {platform_contexts.get(platform, 'social media content creation')}
- Hashtag research and trending topic integration
- Engagement-driven copywriting and call-to-action optimization
- Visual content suggestions and creative direction
- Community management and audience interaction strategies

Create content that feels native to {platform.title()} while serving brand objectives. Always respond in valid JSON format."""

    user_message = f"""Create {post_count} {platform.title()} posts for this campaign:

CAMPAIGN CONCEPT:
Theme: {campaign_brief.get('campaign_concept', {}).get('theme', 'Unknown')}
Key Message: {campaign_brief.get('campaign_concept', {}).get('key_message', 'Unknown')}
Brand Angle: {campaign_brief.get('campaign_concept', {}).get('brand_angle', 'Unknown')}
Call to Action: {campaign_brief.get('campaign_concept', {}).get('call_to_action', 'Unknown')}

BRAND PROFILE:
Brand: {campaign_brief.get('brand_profile', {}).get('brand_name', 'Unknown')}
Voice: {campaign_brief.get('brand_profile', {}).get('brand_voice', 'professional')}
Industry: {campaign_brief.get('brand_profile', {}).get('industry', 'Unknown')}
Core Values: {campaign_brief.get('brand_profile', {}).get('core_values', [])}

TRENDING CONTEXT:
Topic: {campaign_brief.get('topic_name', 'Unknown')}
Trending Analysis: {campaign_brief.get('trending_analysis', {})}

CONTENT PILLARS:
{campaign_brief.get('content_pillars', {})}

Generate {platform.title()} content in this exact JSON structure:

{{
    "posts": [
        {{
            "post_number": 1,
            "content_type": "single_post/carousel/thread/video/story",
            "content_pillar": "educational/promotional/engagement/social_proof",
            "hook": "attention-grabbing opening line",
            "main_content": "primary post content",
            "call_to_action": "specific action request",
            "hashtags": ["relevant", "trending", "hashtags"],
            "mentions": ["@relevant", "@accounts"],
            "visual_suggestion": "detailed visual content description",
            "optimal_timing": "best time to post",
            "engagement_prediction": "predicted engagement level",
            "performance_tips": ["tips to maximize performance"]
        }}
    ],
    "content_calendar": {{
        "posting_schedule": "recommended posting timeline",
        "content_mix": "balance of content types",
        "engagement_strategy": "how to maximize engagement"
    }}
}}"""

    return system_message, user_message


def get_email_campaign_prompt(campaign_brief: Dict[str, Any], email_count: int) -> Tuple[str, str]:
    """Generate system and user prompts for email campaign creation"""
    
    system_message = """You are an email marketing specialist expert in creating high-converting email campaigns that leverage trending topics.

Your expertise includes:
- Email sequence design and customer journey mapping
- Subject line optimization and preview text crafting
- Personalization strategies and dynamic content
- Mobile-responsive email structure and design
- A/B testing frameworks and performance optimization
- Deliverability best practices and list management
- Conversion rate optimization for email campaigns

Create email campaigns that authentically incorporate trending topics while driving business objectives. Always respond in valid JSON format."""

    user_message = f"""Create a {email_count}-email campaign sequence for this trending topic campaign:

CAMPAIGN CONCEPT:
Theme: {campaign_brief.get('campaign_concept', {}).get('theme', 'Unknown')}
Key Message: {campaign_brief.get('campaign_concept', {}).get('key_message', 'Unknown')}
Brand Angle: {campaign_brief.get('campaign_concept', {}).get('brand_angle', 'Unknown')}
Call to Action: {campaign_brief.get('campaign_concept', {}).get('call_to_action', 'Unknown')}

BRAND PROFILE:
Brand: {campaign_brief.get('brand_profile', {}).get('brand_name', 'Unknown')}
Voice: {campaign_brief.get('brand_profile', {}).get('brand_voice', 'professional')}
Industry: {campaign_brief.get('brand_profile', {}).get('industry', 'Unknown')}

AUDIENCE PROFILE:
Demographics: {campaign_brief.get('audience_profile', {}).get('demographics', {})}
Pain Points: {campaign_brief.get('audience_profile', {}).get('pain_points', [])}
Interests: {campaign_brief.get('audience_profile', {}).get('interests', [])}

TRENDING CONTEXT:
Topic: {campaign_brief.get('topic_name', 'Unknown')}
Trending Reason: {campaign_brief.get('trending_analysis', {}).get('trending_analysis', {}).get('trending_reason', {})}

EMAIL STRATEGY:
Type: {campaign_brief.get('channel_strategy', {}).get('email', {}).get('sequence_type', 'nurture')}
Personalization: {campaign_brief.get('channel_strategy', {}).get('email', {}).get('personalization', 'basic')}

Generate the email sequence in this exact JSON structure:

{{
    "email_sequence": [
        {{
            "email_number": 1,
            "email_type": "welcome/nurture/promotional/educational",
            "send_timing": "immediate/1 day/3 days after signup",
            "subject_lines": ["3 compelling subject line options"],
            "preview_text": "email preview text that complements subject",
            "email_structure": {{
                "preheader": "preview text optimization",
                "greeting": "personalized greeting",
                "hook": "trending topic connection and attention grabber",
                "value_proposition": "what the reader gets from this email",
                "main_content": "core email message and content",
                "social_proof": "testimonials, case studies, or credibility indicators",
                "call_to_action": "primary action button text and purpose",
                "secondary_cta": "optional secondary action",
                "closing": "email sign-off and signature",
                "ps": "powerful postscript message"
            }},
            "personalization_tokens": ["{{first_name}}", "{{company}}", "{{interest}}"],
            "mobile_optimization": "mobile-specific formatting notes",
            "a_b_test_variants": {{
                "subject_line_test": "what to test in subject lines",
                "content_test": "what to test in email content",
                "cta_test": "what to test in call-to-action"
            }},
            "expected_metrics": {{
                "open_rate": "predicted open rate %",
                "click_rate": "predicted click rate %",
                "conversion_rate": "predicted conversion rate %"
            }}
        }}
    ],
    "sequence_strategy": {{
        "email_flow": "overall sequence narrative and progression",
        "timing_optimization": "optimal send times and frequency",
        "segmentation": "audience segmentation recommendations",
        "automation_triggers": "behavioral triggers for email sends",
        "follow_up_strategy": "post-sequence engagement plan"
    }},
    "performance_optimization": {{
        "list_building": "strategies to grow email list using this trend",
        "deliverability": "tips to ensure inbox placement",
        "engagement_boosters": "tactics to increase engagement",
        "conversion_optimization": "strategies to maximize conversions"
    }}
}}"""

    return system_message, user_message