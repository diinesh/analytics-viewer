import React, { useState, useEffect } from 'react';
import { TrendingInsights } from '../types';
import { queryAPI } from '../services/api';

interface TrendingInsightsCardProps {
  topicId: number;
  topicName: string;
  onViewFullAnalysis: () => void;
  timeRange?: string;
}

const TrendingInsightsCard: React.FC<TrendingInsightsCardProps> = ({
  topicId,
  topicName,
  onViewFullAnalysis,
  timeRange = '24h'
}) => {
  const [insights, setInsights] = useState<TrendingInsights | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInsights = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const data = await queryAPI.getTopicInsights(topicId, timeRange);
        setInsights(data);
      } catch (err) {
        console.error('Error fetching insights:', err);
        setError(err instanceof Error ? err.message : 'Failed to load insights');
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [topicId, timeRange]);

  if (loading) {
    return (
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        margin: '16px 0'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '200px',
          color: '#666'
        }}>
          <div style={{
            display: 'inline-block',
            width: '24px',
            height: '24px',
            border: '3px solid #f3f3f3',
            borderTop: '3px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <span style={{ marginLeft: '12px' }}>Loading insights...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        margin: '16px 0',
        border: '1px solid #f87171'
      }}>
        <div style={{
          color: '#dc2626',
          textAlign: 'center'
        }}>
          <h3 style={{ margin: '0 0 8px 0' }}>🔍 Insights Unavailable</h3>
          <p style={{ margin: 0, fontSize: '14px' }}>{error}</p>
        </div>
      </div>
    );
  }

  if (!insights) {
    return null;
  }

  const getTrendScoreColor = (score: number) => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  return (
    <div style={{
      backgroundColor: '#fff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      margin: '16px 0',
      border: '1px solid #e5e7eb'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '20px'
      }}>
        <div>
          <h3 style={{
            margin: '0 0 8px 0',
            fontSize: '20px',
            fontWeight: '600',
            color: '#111827'
          }}>
            🔥 Why "{topicName}" is Trending
          </h3>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span style={{ fontSize: '14px', color: '#6b7280' }}>Trend Score:</span>
              <span style={{
                fontWeight: '700',
                fontSize: '18px',
                color: getTrendScoreColor(insights.trend_score)
              }}>
                {insights.trend_score.toFixed(1)}
              </span>
            </div>
            <div style={{
              backgroundColor: '#f3f4f6',
              padding: '4px 12px',
              borderRadius: '20px',
              fontSize: '12px',
              color: '#374151',
              fontWeight: '500'
            }}>
              {insights.analysis_type}
            </div>
          </div>
        </div>

        <button
          onClick={onViewFullAnalysis}
          style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '10px 16px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = '#2563eb';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = '#3b82f6';
          }}
        >
          📊 Full Analysis
        </button>
      </div>

      {/* Content Summary */}
      <div style={{ marginBottom: '20px' }}>
        <h4 style={{
          margin: '0 0 12px 0',
          fontSize: '16px',
          fontWeight: '600',
          color: '#374151',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          📰 Content Summary
        </h4>
        <p style={{
          margin: 0,
          lineHeight: '1.6',
          color: '#4b5563',
          fontSize: '14px',
          backgroundColor: '#f9fafb',
          padding: '16px',
          borderRadius: '8px',
          border: '1px solid #e5e7eb'
        }}>
          {insights.content_summary}
        </p>
      </div>

      {/* Key Themes */}
      {insights.key_themes && insights.key_themes.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{
            margin: '0 0 12px 0',
            fontSize: '16px',
            fontWeight: '600',
            color: '#374151',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            🏷️ Key Themes
          </h4>
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px'
          }}>
            {insights.key_themes.slice(0, 5).map((theme, index) => (
              <span
                key={index}
                style={{
                  backgroundColor: '#dbeafe',
                  color: '#1e40af',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '13px',
                  fontWeight: '500'
                }}
              >
                {theme}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Geographic Focus */}
      {insights.geographic_focus && insights.geographic_focus.length > 0 && (
        <div>
          <h4 style={{
            margin: '0 0 12px 0',
            fontSize: '16px',
            fontWeight: '600',
            color: '#374151',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            🌍 Geographic Hotspots
          </h4>
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px'
          }}>
            {insights.geographic_focus.slice(0, 4).map((location, index) => (
              <span
                key={index}
                style={{
                  backgroundColor: '#dcfce7',
                  color: '#166534',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '13px',
                  fontWeight: '500'
                }}
              >
                {location}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TrendingInsightsCard;