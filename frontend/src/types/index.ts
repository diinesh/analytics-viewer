export interface QueryResponse {
  sql: string;
  data: Array<Record<string, any>>;
  chart_type: string;
  title: string;
}

export interface QueryRequest {
  query: string;
}

// Trending Analysis Types
export interface TrendingInsights {
  topic_name: string;
  trend_score: number;
  content_summary: string;
  key_themes: string[];
  geographic_focus: string[];
  analysis_type: string;
}

export interface TrendingReason {
  primary_cause: string;
  specific_event: string;
  timing_factor: string;
}

export interface ContentAnalysis {
  content_type: string;
  story_summary: string;
  key_drivers: string[];
  viral_factors: string[];
}

export interface TrendPatterns {
  velocity: string;
  momentum: string;
  geographic_insight: string;
  demographic_appeal: string;
}

export interface BusinessContext {
  category_fit: string;
  business_relevance: string;
  market_impact: string;
}

export interface TrendPrediction {
  trend_duration: string;
  peak_prediction: string;
  related_trends: string;
}

export interface TrendingAnalysis {
  trending_reason: TrendingReason;
  content_analysis: ContentAnalysis;
  trend_patterns: TrendPatterns;
  business_context: BusinessContext;
  prediction: TrendPrediction;
}

export interface PopularityDistribution {
  distribution_data: {
    category_breakdown: Record<string, number>;
    business_breakdown: Record<string, number>;
    geographic_breakdown: Record<string, number>;
    stat_type_breakdown: Record<string, number>;
  };
  analysis: {
    category_analysis: any;
    business_analysis: any;
    geographic_analysis: any;
    engagement_analysis: any;
  };
}

export interface ContentSummary {
  topic_overview: {
    what_it_is: string;
    why_notable: string;
    context: string;
  };
  content_themes: {
    primary_themes: string[];
    secondary_themes: string[];
    emotional_tone: string;
  };
  stakeholders: {
    key_people: string[];
    organizations: string[];
    affected_parties: string[];
  };
  timeline: {
    key_events: string;
    current_status: string;
    what_next: string;
  };
  significance: {
    immediate_impact: string;
    broader_implications: string;
    historical_context: string;
  };
}

export interface WebContext {
  search_query: string;
  search_results: any;
  content_summary: string;
  key_themes: string[];
  search_timestamp: string;
}

export interface TopicInfo {
  topic_id: number;
  topic_name: string;
  category: string;
  business: string;
  analysis_timestamp: string;
}

export interface ComprehensiveAnalysis {
  topic_info: TopicInfo;
  trending_analysis: TrendingAnalysis;
  popularity_distribution: PopularityDistribution;
  content_summary: ContentSummary;
  web_context: WebContext;
  raw_data: Record<string, any>;
}