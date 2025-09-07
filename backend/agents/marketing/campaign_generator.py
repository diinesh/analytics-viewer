"""
Marketing Campaign Generator - Creates comprehensive marketing campaigns from trending topics
"""
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..analysis.trending_agent import TrendingAnalysisAgent
from ..integrations.openai_client import openai_client
from ..prompts.marketing_prompts import (
    get_campaign_strategy_prompt,
    get_social_media_content_prompt,
    get_email_campaign_prompt
)
from .models import (
    BrandProfile, AudienceProfile, CampaignRequest, CampaignBrief,
    CampaignContent, SocialPost, EmailContent, Platform, ContentType, CampaignGoal
)


class MarketingCampaignGenerator:
    """
    Main marketing campaign generator that creates comprehensive campaigns from trending topics
    """
    
    def __init__(self):
        self.trending_agent = TrendingAnalysisAgent()
        self.openai_client = openai_client
    
    async def generate_complete_campaign(self, campaign_request: CampaignRequest) -> Dict[str, Any]:
        """
        Generate a complete marketing campaign from a trending topic
        
        Args:
            campaign_request: Campaign generation request with brand/audience info
            
        Returns:
            Complete campaign with strategy, content, and calendar
        """
        try:
            print(f"Starting campaign generation for topic ID: {campaign_request.topic_id}")
            
            # Step 1: Get trending analysis
            trending_analysis = await self.trending_agent.analyze_topic_trending(
                campaign_request.topic_id, "24h"
            )
            
            if "error" in trending_analysis:
                return {"error": f"Failed to get trending analysis: {trending_analysis['error']}"}
            
            # Step 2: Generate campaign strategy
            print("Generating campaign strategy...")
            campaign_brief = await self._generate_campaign_brief(
                campaign_request, trending_analysis
            )
            
            # Step 3: Generate content for each channel
            print("Generating campaign content...")
            campaign_content = await self._generate_campaign_content(campaign_brief)
            
            # Step 4: Create content calendar
            content_calendar = await self._create_content_calendar(campaign_brief, campaign_content)
            
            complete_campaign = {
                "campaign_id": campaign_brief.campaign_id,
                "campaign_brief": self._serialize_campaign_brief(campaign_brief),
                "campaign_content": self._serialize_campaign_content(campaign_content),
                "content_calendar": content_calendar,
                "performance_predictions": await self._predict_performance(campaign_brief, campaign_content),
                "budget_breakdown": await self._calculate_budget(campaign_brief),
                "generated_at": datetime.now().isoformat()
            }
            
            print("Campaign generation completed successfully")
            return complete_campaign
            
        except Exception as e:
            print(f"ERROR in generate_complete_campaign: {str(e)}")
            return {
                "error": f"Campaign generation failed: {str(e)}",
                "topic_id": campaign_request.topic_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_campaign_brief(
        self, 
        request: CampaignRequest, 
        trending_analysis: Dict[str, Any]
    ) -> CampaignBrief:
        """Generate comprehensive campaign strategy and brief"""
        
        if not self.openai_client.is_available():
            raise Exception("OpenAI not available for campaign generation")
        
        # Prepare data for prompt
        brand_data = {
            "brand_name": request.brand_profile.brand_name,
            "industry": request.brand_profile.industry,
            "business_vertical": request.brand_profile.business_vertical,
            "brand_voice": request.brand_profile.brand_voice,
            "core_values": request.brand_profile.core_values,
            "target_markets": request.brand_profile.target_markets,
            "prohibited_topics": request.brand_profile.prohibited_topics
        }
        
        audience_data = {
            "demographics": request.audience_profile.demographics,
            "interests": request.audience_profile.interests,
            "pain_points": request.audience_profile.pain_points,
            "preferred_platforms": request.audience_profile.preferred_platforms,
            "content_preferences": request.audience_profile.content_preferences,
            "geographic_focus": request.audience_profile.geographic_focus
        }
        
        # Generate campaign strategy
        system_message, user_message = get_campaign_strategy_prompt(
            trending_analysis, brand_data, audience_data
        )
        
        strategy_response = await self.openai_client.generate_completion_with_system(
            system_message, user_message
        )
        
        try:
            strategy = json.loads(strategy_response)
        except json.JSONDecodeError:
            raise Exception(f"Failed to parse campaign strategy: {strategy_response[:200]}...")
        
        # Create campaign brief
        campaign_brief = CampaignBrief(
            campaign_id=str(uuid.uuid4()),
            topic_id=request.topic_id,
            topic_name=trending_analysis.get("topic_info", {}).get("topic_name", "Unknown"),
            brand_profile=request.brand_profile,
            audience_profile=request.audience_profile,
            campaign_goals=[CampaignGoal(goal) for goal in request.campaign_goals],
            channels=[Platform(channel) for channel in request.channels],
            trending_analysis=trending_analysis,
            campaign_concept=strategy.get("campaign_concept", {}),
            channel_strategy=strategy.get("channel_strategy", {}),
            content_pillars=strategy.get("content_pillars", {}),
            success_metrics=strategy.get("success_metrics", {}),
            created_at=datetime.now(),
            budget=request.budget,
            duration_days=request.duration_days
        )
        
        return campaign_brief
    
    async def _generate_campaign_content(self, campaign_brief: CampaignBrief) -> CampaignContent:
        """Generate content for all requested channels"""
        
        social_posts = []
        email_campaigns = []
        blog_content = []
        visual_assets = []
        
        # Prepare campaign data for prompts
        brief_data = {
            "campaign_concept": campaign_brief.campaign_concept,
            "brand_profile": {
                "brand_name": campaign_brief.brand_profile.brand_name,
                "brand_voice": campaign_brief.brand_profile.brand_voice,
                "industry": campaign_brief.brand_profile.industry,
                "core_values": campaign_brief.brand_profile.core_values
            },
            "audience_profile": {
                "demographics": campaign_brief.audience_profile.demographics,
                "interests": campaign_brief.audience_profile.interests,
                "pain_points": campaign_brief.audience_profile.pain_points
            },
            "topic_name": campaign_brief.topic_name,
            "trending_analysis": campaign_brief.trending_analysis,
            "content_pillars": campaign_brief.content_pillars
        }
        
        # Generate social media content
        for platform in campaign_brief.channels:
            if platform in [Platform.LINKEDIN, Platform.TWITTER, Platform.INSTAGRAM, Platform.TIKTOK]:
                platform_posts = await self._generate_social_content(brief_data, platform.value)
                social_posts.extend(platform_posts)
        
        # Generate email content
        if Platform.EMAIL in campaign_brief.channels:
            email_content = await self._generate_email_content(brief_data)
            email_campaigns.extend(email_content)
        
        # Generate blog content suggestions
        if Platform.BLOG in campaign_brief.channels:
            blog_content = await self._generate_blog_content(brief_data)
        
        return CampaignContent(
            campaign_id=campaign_brief.campaign_id,
            social_posts=social_posts,
            email_campaigns=email_campaigns,
            blog_content=blog_content,
            visual_assets=visual_assets,
            content_calendar={},
            performance_predictions={},
            generated_at=datetime.now()
        )
    
    async def _generate_social_content(self, brief_data: Dict[str, Any], platform: str) -> List[SocialPost]:
        """Generate social media content for a specific platform"""
        
        post_counts = {
            "linkedin": 5,
            "twitter": 8,
            "instagram": 6,
            "tiktok": 4
        }
        
        post_count = post_counts.get(platform, 5)
        
        system_message, user_message = get_social_media_content_prompt(
            brief_data, platform, post_count
        )
        
        content_response = await self.openai_client.generate_completion_with_system(
            system_message, user_message
        )
        
        try:
            content_data = json.loads(content_response)
            posts = []
            
            # Content type mapping for API response variations
            content_type_mapping = {
                "carousel": "carousel_post",
                "single_post": "single_post",
                "thread": "thread",
                "video": "video", 
                "story": "story"
            }
            
            for post_data in content_data.get("posts", []):
                raw_content_type = post_data.get("content_type", "single_post")
                mapped_content_type = content_type_mapping.get(raw_content_type, "single_post")
                
                post = SocialPost(
                    platform=Platform(platform),
                    content_type=ContentType(mapped_content_type),
                    hook=post_data.get("hook", ""),
                    body=post_data.get("main_content", ""),
                    cta=post_data.get("call_to_action", ""),
                    hashtags=post_data.get("hashtags", []),
                    mentions=post_data.get("mentions", []),
                    visual_suggestion=post_data.get("visual_suggestion", ""),
                    optimal_timing=post_data.get("optimal_timing", ""),
                    character_count=len(post_data.get("main_content", "")),
                    engagement_prediction=7.5  # Default prediction
                )
                posts.append(post)
            
            return posts
            
        except json.JSONDecodeError:
            print(f"Failed to parse {platform} content: {content_response[:200]}...")
            return []
    
    async def _generate_email_content(self, brief_data: Dict[str, Any]) -> List[EmailContent]:
        """Generate email campaign content"""
        
        email_count = 3  # Default 3-email sequence
        
        system_message, user_message = get_email_campaign_prompt(brief_data, email_count)
        
        email_response = await self.openai_client.generate_completion_with_system(
            system_message, user_message
        )
        
        try:
            email_data = json.loads(email_response)
            emails = []
            
            for email_info in email_data.get("email_sequence", []):
                email = EmailContent(
                    email_number=email_info.get("email_number", 1),
                    email_type=email_info.get("email_type", "nurture"),
                    subject_lines=email_info.get("subject_lines", []),
                    preview_text=email_info.get("preview_text", ""),
                    email_structure=email_info.get("email_structure", {}),
                    send_timing=email_info.get("send_timing", "1 day"),
                    personalization_tokens=email_info.get("personalization_tokens", []),
                    expected_open_rate=email_info.get("expected_metrics", {}).get("open_rate", 25.0),
                    expected_click_rate=email_info.get("expected_metrics", {}).get("click_rate", 3.5)
                )
                emails.append(email)
            
            return emails
            
        except json.JSONDecodeError:
            print(f"Failed to parse email content: {email_response[:200]}...")
            return []
    
    async def _generate_blog_content(self, brief_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate blog content suggestions"""
        
        # Simple blog content suggestions based on campaign
        return [
            {
                "title": f"Understanding the {brief_data['topic_name']} Trend: What It Means for {brief_data['brand_profile']['industry']}",
                "type": "thought_leadership",
                "word_count": 1500,
                "seo_keywords": [brief_data['topic_name'].lower(), brief_data['brand_profile']['industry']],
                "outline": [
                    "Introduction to the trending topic",
                    "Why it matters to our industry",
                    "Practical implications and opportunities",
                    "How to take advantage of this trend",
                    "Future predictions and recommendations"
                ]
            }
        ]
    
    async def _create_content_calendar(
        self, 
        campaign_brief: CampaignBrief, 
        campaign_content: CampaignContent
    ) -> Dict[str, Any]:
        """Create a content publishing calendar"""
        
        calendar = {
            "campaign_duration": campaign_brief.duration_days,
            "total_pieces": len(campaign_content.social_posts) + len(campaign_content.email_campaigns),
            "posting_schedule": {
                "week_1": {
                    "social_posts": len([p for p in campaign_content.social_posts if p.platform in [Platform.TWITTER, Platform.LINKEDIN]]),
                    "emails": 1
                },
                "week_2": {
                    "social_posts": len([p for p in campaign_content.social_posts if p.platform in [Platform.INSTAGRAM, Platform.TIKTOK]]),
                    "emails": 2
                }
            },
            "optimal_times": {
                "linkedin": "Tuesday-Thursday 8-10am",
                "twitter": "Monday-Friday 12-3pm", 
                "instagram": "Wednesday-Friday 11am-2pm",
                "email": "Tuesday/Thursday 10am"
            }
        }
        
        return calendar
    
    async def _predict_performance(
        self, 
        campaign_brief: CampaignBrief, 
        campaign_content: CampaignContent
    ) -> Dict[str, Any]:
        """Predict campaign performance metrics"""
        
        return {
            "reach_prediction": {
                "social_media": 15000,
                "email": 500,
                "total_impressions": 25000
            },
            "engagement_prediction": {
                "social_engagement_rate": 4.2,
                "email_open_rate": 24.5,
                "email_click_rate": 3.8
            },
            "conversion_prediction": {
                "leads_generated": 45,
                "conversion_rate": 2.1,
                "roi_estimate": 3.2
            }
        }
    
    async def _calculate_budget(self, campaign_brief: CampaignBrief) -> Dict[str, Any]:
        """Calculate budget breakdown for campaign"""
        
        if not campaign_brief.budget:
            return {"message": "No budget specified"}
        
        budget = campaign_brief.budget
        return {
            "total_budget": budget,
            "content_creation": budget * 0.4,
            "paid_promotion": budget * 0.35,
            "tools_analytics": budget * 0.15,
            "contingency": budget * 0.1
        }
    
    def _serialize_campaign_brief(self, brief: CampaignBrief) -> Dict[str, Any]:
        """Convert campaign brief to serializable dict"""
        return {
            "campaign_id": brief.campaign_id,
            "topic_id": brief.topic_id,
            "topic_name": brief.topic_name,
            "brand_name": brief.brand_profile.brand_name,
            "campaign_goals": [goal.value for goal in brief.campaign_goals],
            "channels": [channel.value for channel in brief.channels],
            "campaign_concept": brief.campaign_concept,
            "channel_strategy": brief.channel_strategy,
            "content_pillars": brief.content_pillars,
            "success_metrics": brief.success_metrics,
            "created_at": brief.created_at.isoformat(),
            "duration_days": brief.duration_days
        }
    
    def _serialize_campaign_content(self, content: CampaignContent) -> Dict[str, Any]:
        """Convert campaign content to serializable dict"""
        return {
            "campaign_id": content.campaign_id,
            "social_posts": [
                {
                    "platform": post.platform.value,
                    "content_type": post.content_type.value,
                    "hook": post.hook,
                    "body": post.body,
                    "cta": post.cta,
                    "hashtags": post.hashtags,
                    "mentions": post.mentions,
                    "visual_suggestion": post.visual_suggestion,
                    "optimal_timing": post.optimal_timing,
                    "engagement_prediction": post.engagement_prediction
                }
                for post in content.social_posts
            ],
            "email_campaigns": [
                {
                    "email_number": email.email_number,
                    "email_type": email.email_type,
                    "subject_lines": email.subject_lines,
                    "preview_text": email.preview_text,
                    "email_structure": email.email_structure,
                    "send_timing": email.send_timing,
                    "expected_open_rate": email.expected_open_rate,
                    "expected_click_rate": email.expected_click_rate
                }
                for email in content.email_campaigns
            ],
            "blog_content": content.blog_content,
            "generated_at": content.generated_at.isoformat()
        }


# Global instance
campaign_generator = MarketingCampaignGenerator()