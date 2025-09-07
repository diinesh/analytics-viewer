"""
Data models for marketing campaign system
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CampaignGoal(Enum):
    BRAND_AWARENESS = "brand_awareness"
    LEAD_GENERATION = "lead_generation"
    ENGAGEMENT = "engagement"
    SALES = "sales"
    THOUGHT_LEADERSHIP = "thought_leadership"


class Platform(Enum):
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    EMAIL = "email"
    BLOG = "blog"


class ContentType(Enum):
    SINGLE_POST = "single_post"
    CAROUSEL = "carousel_post"
    THREAD = "thread"
    VIDEO = "video"
    STORY = "story"
    EMAIL_SEQUENCE = "email_sequence"
    BLOG_POST = "blog_post"


@dataclass
class BrandProfile:
    brand_name: str
    industry: str
    business_vertical: str
    brand_voice: str  # "professional", "casual", "witty", "authoritative"
    target_markets: List[str]
    core_values: List[str]
    prohibited_topics: List[str]
    website_url: Optional[str] = None
    logo_url: Optional[str] = None


@dataclass
class AudienceProfile:
    demographics: Dict[str, Any]
    interests: List[str]
    pain_points: List[str]
    preferred_platforms: List[str]
    content_preferences: List[str]
    geographic_focus: List[str]
    age_range: Optional[str] = None
    income_level: Optional[str] = None


@dataclass
class CampaignBrief:
    campaign_id: str
    topic_id: int
    topic_name: str
    brand_profile: BrandProfile
    audience_profile: AudienceProfile
    campaign_goals: List[CampaignGoal]
    channels: List[Platform]
    trending_analysis: Dict[str, Any]
    campaign_concept: Dict[str, Any]
    channel_strategy: Dict[str, Any]
    content_pillars: Dict[str, Any]
    success_metrics: Dict[str, Any]
    created_at: datetime
    budget: Optional[float] = None
    duration_days: Optional[int] = None


@dataclass
class SocialPost:
    platform: Platform
    content_type: ContentType
    hook: str
    body: str
    cta: str
    hashtags: List[str]
    mentions: List[str]
    visual_suggestion: str
    optimal_timing: str
    character_count: Optional[int] = None
    engagement_prediction: Optional[float] = None


@dataclass
class EmailContent:
    email_number: int
    email_type: str
    subject_lines: List[str]
    preview_text: str
    email_structure: Dict[str, str]
    send_timing: str
    personalization_tokens: List[str]
    expected_open_rate: Optional[float] = None
    expected_click_rate: Optional[float] = None


@dataclass
class CampaignContent:
    campaign_id: str
    social_posts: List[SocialPost]
    email_campaigns: List[EmailContent]
    blog_content: List[Dict[str, Any]]
    visual_assets: List[Dict[str, Any]]
    content_calendar: Dict[str, Any]
    performance_predictions: Dict[str, Any]
    generated_at: datetime


@dataclass
class CampaignRequest:
    topic_id: int
    brand_profile: BrandProfile
    audience_profile: AudienceProfile
    campaign_goals: List[str]
    channels: List[str]
    budget: Optional[float] = None
    duration_days: Optional[int] = 7
    urgent: bool = False


@dataclass
class ContentGenerationRequest:
    campaign_brief: CampaignBrief
    content_types: List[ContentType]
    quantity: Dict[str, int]  # {"social_posts": 10, "emails": 3}
    tone_adjustments: Optional[Dict[str, str]] = None