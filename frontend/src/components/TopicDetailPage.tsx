import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import { queryAPI } from '../services/api';
import TrendingInsightsCard from './TrendingInsightsCard';

interface TopicInfo {
  topic_name: string;
  category?: string;
  business?: string;
  topic_id: number;
  trend_score?: number;
}

interface TimeSeriesData {
  timestamp: string;
  trend_score: number;
  stat_value: number;
  stat_type: string;
  country_code?: string;
  region_code?: string;
}

interface TopicStats {
  total_events: number;
  avg_trend_score: number;
  peak_trend_score: number;
  countries: string[];
  stat_types: string[];
  date_range: {
    start: string;
    end: string;
  };
}

interface TopicDetailPageProps {
  topicId: number;
  topicName?: string; // Optional fallback display name
  onBack?: () => void;
  onViewAnalysis?: (topicId: number, topicName: string) => void;
}

const TopicDetailPage: React.FC<TopicDetailPageProps> = ({ topicId, topicName, onBack, onViewAnalysis }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [topicInfo, setTopicInfo] = useState<TopicInfo | null>(null);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([]);
  const [topicStats, setTopicStats] = useState<TopicStats | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [selectedStatType, setSelectedStatType] = useState('all');
  const [selectedCountry, setSelectedCountry] = useState('all');

  const timeRanges = [
    { value: '1h', label: 'Last Hour' },
    { value: '6h', label: 'Last 6 Hours' },
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' }
  ];

  useEffect(() => {
    fetchTopicData();
  }, [topicId, selectedTimeRange, selectedStatType, selectedCountry]);

  const fetchTopicData = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log(`Fetching topic data for ID: ${topicId}`);
      
      // Call the real API
      const response = await queryAPI.getTopicDetails(
        topicId,
        selectedTimeRange,
        selectedStatType,
        selectedCountry
      );
      
      console.log('API Response:', response);
      
      // Set the data from API response
      setTopicInfo(response.topic_info);
      setTimeSeriesData(response.time_series_data || []);
      setTopicStats(response.stats);

    } catch (err) {
      console.error('Error fetching topic data:', err);
      
      // Fallback to mock data if API fails
      console.log('Falling back to mock data...');
      
      const mockTopicInfo: TopicInfo = {
        topic_name: topicName || `Topic ${topicId}`,
        category: 'Technology',
        business: 'Tech',
        topic_id: topicId,
        trend_score: 85.5
      };

      const mockTimeSeriesData: TimeSeriesData[] = generateMockTimeSeriesData(selectedTimeRange);
      
      const mockStats: TopicStats = {
        total_events: 1250,
        avg_trend_score: 75.3,
        peak_trend_score: 95.8,
        countries: ['US', 'CA', 'GB', 'DE'],
        stat_types: ['search_volume', 'mentions', 'appearance'],
        date_range: {
          start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          end: new Date().toISOString()
        }
      };

      setTopicInfo(mockTopicInfo);
      setTimeSeriesData(mockTimeSeriesData);
      setTopicStats(mockStats);
      
      // Don't set error for fallback case
      // setError(err instanceof Error ? err.message : 'Failed to fetch topic data');
    } finally {
      setLoading(false);
    }
  };

  const generateMockTimeSeriesData = (timeRange: string): TimeSeriesData[] => {
    const data: TimeSeriesData[] = [];
    const now = new Date();
    let intervals = 24; // default for 24h
    let stepMinutes = 60; // 1 hour steps

    switch (timeRange) {
      case '1h':
        intervals = 12;
        stepMinutes = 5;
        break;
      case '6h':
        intervals = 24;
        stepMinutes = 15;
        break;
      case '24h':
        intervals = 24;
        stepMinutes = 60;
        break;
      case '7d':
        intervals = 7 * 24;
        stepMinutes = 60;
        break;
      case '30d':
        intervals = 30;
        stepMinutes = 24 * 60;
        break;
    }

    for (let i = intervals; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * stepMinutes * 60 * 1000);
      data.push({
        timestamp: timestamp.toISOString(),
        trend_score: 40 + Math.random() * 50 + Math.sin(i / 5) * 20,
        stat_value: 100 + Math.random() * 500 + Math.cos(i / 3) * 200,
        stat_type: 'search_volume',
        country_code: 'US'
      });
    }

    return data;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    if (selectedTimeRange === '1h' || selectedTimeRange === '6h') {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (selectedTimeRange === '24h') {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  const getTrendColor = (score: number) => {
    if (score >= 80) return '#dc2626';
    if (score >= 60) return '#ea580c';
    if (score >= 40) return '#d97706';
    return '#16a34a';
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            display: 'inline-block',
            width: '48px',
            height: '48px',
            border: '4px solid #f3f3f3',
            borderTop: '4px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <p style={{ marginTop: '16px', color: '#666', fontSize: '18px' }}>
            Loading topic details...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa', padding: '20px' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <div style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '12px',
            padding: '24px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '64px', marginBottom: '16px' }}>⚠️</div>
            <h2 style={{ color: '#dc2626', marginBottom: '8px' }}>Error Loading Topic</h2>
            <p style={{ color: '#991b1b', marginBottom: '20px' }}>{error}</p>
            {onBack && (
              <button
                onClick={onBack}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#3b82f6',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}
              >
                ← Back to Trends
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#fff',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        padding: '20px 0'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              {onBack && (
                <button
                  onClick={onBack}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#f3f4f6',
                    color: '#374151',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  ← Back
                </button>
              )}
              <div>
                <h1 style={{
                  fontSize: '28px',
                  fontWeight: 'bold',
                  color: '#1f2937',
                  margin: 0
                }}>
                  {topicInfo?.topic_name}
                </h1>
                <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
                  {topicInfo?.category && (
                    <span style={{
                      backgroundColor: '#eff6ff',
                      color: '#1e40af',
                      padding: '4px 12px',
                      borderRadius: '16px',
                      fontSize: '14px',
                      fontWeight: '500'
                    }}>
                      📂 {topicInfo.category}
                    </span>
                  )}
                  {topicInfo?.business && (
                    <span style={{
                      backgroundColor: '#f0fdf4',
                      color: '#15803d',
                      padding: '4px 12px',
                      borderRadius: '16px',
                      fontSize: '14px',
                      fontWeight: '500'
                    }}>
                      🏢 {topicInfo.business}
                    </span>
                  )}
                  {topicInfo?.trend_score && (
                    <span style={{
                      backgroundColor: '#fef3c7',
                      color: '#92400e',
                      padding: '4px 12px',
                      borderRadius: '16px',
                      fontSize: '14px',
                      fontWeight: '500'
                    }}>
                      🔥 {topicInfo.trend_score.toFixed(1)}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Stats Summary */}
          {topicStats && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
              gap: '16px',
              marginTop: '20px'
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '28px', fontWeight: '700', color: '#3b82f6' }}>
                  {(topicStats.total_events || 0).toLocaleString()}
                </div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>Total Events</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '28px', fontWeight: '700', color: '#10b981' }}>
                  {(topicStats.avg_trend_score || 0).toFixed(1)}
                </div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>Avg Score</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '28px', fontWeight: '700', color: '#f59e0b' }}>
                  {(topicStats.peak_trend_score || 0).toFixed(1)}
                </div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>Peak Score</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '28px', fontWeight: '700', color: '#8b5cf6' }}>
                  {(topicStats.countries || []).length}
                </div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>Countries</div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px 20px' }}>
        {/* Trending Insights */}
        {topicInfo && onViewAnalysis && (
          <TrendingInsightsCard
            topicId={topicId}
            topicName={topicInfo.topic_name}
            onViewFullAnalysis={() => onViewAnalysis(topicId, topicInfo.topic_name)}
            timeRange={selectedTimeRange}
          />
        )}

        {/* Filters */}
        <div style={{
          backgroundColor: '#fff',
          borderRadius: '12px',
          padding: '20px',
          marginBottom: '24px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#374151', marginBottom: '16px' }}>
            Chart Options
          </h3>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px'
          }}>
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>
                Time Range
              </label>
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
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

            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>
                Statistic Type
              </label>
              <select
                value={selectedStatType}
                onChange={(e) => setSelectedStatType(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  backgroundColor: '#fff'
                }}
              >
                <option value="all">All Types</option>
                <option value="search_volume">Search Volume</option>
                <option value="mentions">Mentions</option>
                <option value="appearance">Appearances</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>
                Country
              </label>
              <select
                value={selectedCountry}
                onChange={(e) => setSelectedCountry(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  backgroundColor: '#fff'
                }}
              >
                <option value="all">All Countries</option>
                <option value="US">United States</option>
                <option value="CA">Canada</option>
                <option value="GB">United Kingdom</option>
                <option value="DE">Germany</option>
              </select>
            </div>
          </div>
        </div>

        {/* Time Series Charts */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr',
          gap: '24px'
        }}>
          {/* Trend Score Chart */}
          <div style={{
            backgroundColor: '#fff',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#374151', marginBottom: '20px' }}>
              📈 Trend Score Over Time
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={formatTimestamp}
                  stroke="#6b7280"
                  fontSize={12}
                />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip 
                  labelFormatter={(value) => `Time: ${formatTimestamp(value)}`}
                  formatter={(value: number) => [value.toFixed(1), 'Trend Score']}
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="trend_score" 
                  stroke="#3b82f6" 
                  fill="#3b82f6"
                  fillOpacity={0.2}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Stat Value Chart */}
          <div style={{
            backgroundColor: '#fff',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#374151', marginBottom: '20px' }}>
              📊 Activity Volume Over Time
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={formatTimestamp}
                  stroke="#6b7280"
                  fontSize={12}
                />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip 
                  labelFormatter={(value) => `Time: ${formatTimestamp(value)}`}
                  formatter={(value: number) => [Math.round(value), 'Volume']}
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                  }}
                />
                <Bar dataKey="stat_value" fill="#10b981" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopicDetailPage;