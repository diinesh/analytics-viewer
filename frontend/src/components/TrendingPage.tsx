import React, { useState, useEffect } from 'react';
import { queryAPI } from '../services/api';
import TrendsGrid from './TrendsGrid';

interface TrendingFilters {
  timeRange: string;
  category: string;
  country: string;
  business: string;
}

interface TrendingTopic {
  topic_id?: number;
  topic_name: string;
  category?: string;
  business?: string;
  country_code?: string;
  avg_trend_score: number;
  peak_trend_score?: number;
  total_volume?: number;
  event_count?: number;
}

interface TrendingPageProps {
  onNavigateToQuery?: () => void;
  onTopicClick?: (topicId: number, topicName: string) => void;
}

const TrendingPage: React.FC<TrendingPageProps> = ({ onNavigateToQuery, onTopicClick }) => {
  const [loading, setLoading] = useState(false);
  const [trends, setTrends] = useState<TrendingTopic[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  const [filters, setFilters] = useState<TrendingFilters>({
    timeRange: '24h',
    category: '',
    country: '',
    business: ''
  });

  const timeRanges = [
    { value: '15m', label: 'Last 15 minutes' },
    { value: '1h', label: 'Last hour' },
    { value: '6h', label: 'Last 6 hours' },
    { value: '24h', label: 'Last 24 hours' },
    { value: '7d', label: 'Last 7 days' }
  ];

  const categories = [
    { value: '', label: 'All Categories' },
    { value: 'technology', label: 'Technology' },
    { value: 'sports', label: 'Sports' },
    { value: 'entertainment', label: 'Entertainment' },
    { value: 'politics', label: 'Politics' },
    { value: 'business', label: 'Business' },
    { value: 'health', label: 'Health' },
    { value: 'science', label: 'Science' }
  ];

  const countries = [
    { value: '', label: 'All Countries' },
    { value: 'US', label: 'United States' },
    { value: 'CA', label: 'Canada' },
    { value: 'GB', label: 'United Kingdom' },
    { value: 'DE', label: 'Germany' },
    { value: 'FR', label: 'France' },
    { value: 'JP', label: 'Japan' },
    { value: 'AU', label: 'Australia' }
  ];

  const businesses = [
    { value: '', label: 'All Business Verticals' },
    { value: 'tech', label: 'Technology' },
    { value: 'finance', label: 'Finance' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'retail', label: 'Retail' },
    { value: 'media', label: 'Media' },
    { value: 'automotive', label: 'Automotive' },
    { value: 'education', label: 'Education' }
  ];

  const buildTrendingQuery = (filters: TrendingFilters): string => {
    const timeMapping: { [key: string]: string } = {
      '15m': '15 MINUTE',
      '1h': '1 HOUR', 
      '6h': '6 HOUR',
      '24h': '24 HOUR',
      '7d': '7 DAY'
    };

    let query = "Show me trending topics";
    
    // Add time filter
    const timeInterval = timeMapping[filters.timeRange] || '24 HOUR';
    query += ` in the last ${timeInterval.toLowerCase()}`;
    
    // Add optional filters
    const filterParts: string[] = [];
    
    if (filters.country) {
      const countryName = countries.find(c => c.value === filters.country)?.label || filters.country;
      filterParts.push(`in ${countryName}`);
    }
    
    if (filters.category) {
      filterParts.push(`in ${filters.category} category`);
    }
    
    if (filters.business) {
      const businessName = businesses.find(b => b.value === filters.business)?.label || filters.business;
      filterParts.push(`for ${businessName} business vertical`);
    }
    
    if (filterParts.length > 0) {
      query += ` ${filterParts.join(', ')}`;
    }
    
    return query;
  };

  const fetchTrends = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const naturalQuery = buildTrendingQuery(filters);
      console.log('Generated query:', naturalQuery);
      
      const response = await queryAPI.processQuery(naturalQuery);
      
      // Parse the response data into trending topics
      const trendingTopics: TrendingTopic[] = response.data.map((item: any, index: number) => {
        // Log the raw data to debug topic_id issues
        console.log(`Topic ${index + 1}:`, item);
        
        return {
          topic_id: item.topic_id, // Use only the actual topic_id from database, no fallback
          topic_name: item.topic_name || 'Unknown',
          category: item.category,
          business: item.business,
          country_code: item.country_code,
          avg_trend_score: item.avg_trend_score || 0,
          peak_trend_score: item.peak_trend_score,
          total_volume: item.total_volume,
          event_count: item.event_count
        };
      });
      
      setTrends(trendingTopics);
    } catch (err) {
      console.error('Error fetching trends:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch trending topics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends();
  }, [filters]);

  const handleFilterChange = (key: keyof TrendingFilters, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };


  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#fff',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        padding: '20px 0'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h1 style={{
                fontSize: '32px',
                fontWeight: 'bold',
                color: '#333',
                margin: '0 0 8px 0'
              }}>
                Trending Topics
              </h1>
              <p style={{ color: '#666', margin: 0, fontSize: '16px' }}>
                Discover what's trending across different categories, countries, and business verticals
              </p>
            </div>
            
            {/* Navigation */}
            <nav style={{ display: 'flex', gap: '8px' }}>
              <button
                style={{
                  padding: '10px 20px',
                  borderRadius: '8px',
                  border: 'none',
                  backgroundColor: '#3b82f6',
                  color: '#fff',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                📈 Trending
              </button>
              <button
                onClick={() => onNavigateToQuery?.()}
                style={{
                  padding: '10px 20px',
                  borderRadius: '8px',
                  border: 'none',
                  backgroundColor: '#f3f4f6',
                  color: '#374151',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                🔍 Query
              </button>
            </nav>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        {/* Filters */}
        <div style={{
          backgroundColor: '#fff',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '24px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#333', marginBottom: '16px' }}>
            Filter Options
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px'
          }}>
            {/* Time Range */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>
                Time Range
              </label>
              <select
                value={filters.timeRange}
                onChange={(e) => handleFilterChange('timeRange', e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  backgroundColor: '#fff'
                }}
              >
                {timeRanges.map(range => (
                  <option key={range.value} value={range.value}>
                    {range.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Category */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>
                Category
              </label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  backgroundColor: '#fff'
                }}
              >
                {categories.map(cat => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Country */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>
                Country
              </label>
              <select
                value={filters.country}
                onChange={(e) => handleFilterChange('country', e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  backgroundColor: '#fff'
                }}
              >
                {countries.map(country => (
                  <option key={country.value} value={country.value}>
                    {country.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Business */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>
                Business Vertical
              </label>
              <select
                value={filters.business}
                onChange={(e) => handleFilterChange('business', e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  backgroundColor: '#fff'
                }}
              >
                {businesses.map(biz => (
                  <option key={biz.value} value={biz.value}>
                    {biz.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Trending Topics Grid */}
        <TrendsGrid 
          trends={trends}
          loading={loading}
          error={error}
          onTopicClick={(topic) => {
            console.log('Clicked topic:', topic.topic_name, 'ID:', topic.topic_id);
            if (topic.topic_id && typeof topic.topic_id === 'number') {
              onTopicClick?.(topic.topic_id, topic.topic_name);
            } else {
              console.warn('Cannot navigate - invalid topic_id:', topic.topic_id);
            }
          }}
        />
      </div>
    </div>
  );
};

export default TrendingPage;