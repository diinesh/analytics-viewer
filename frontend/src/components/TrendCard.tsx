import React from 'react';

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

interface TrendCardProps {
  topic: TrendingTopic;
  rank: number;
  onClick?: (topic: TrendingTopic) => void;
}

const TrendCard: React.FC<TrendCardProps> = ({ topic, rank, onClick }) => {
  const getTrendScoreColor = (score: number): string => {
    if (score >= 80) return '#dc2626'; // Red for very hot
    if (score >= 60) return '#ea580c'; // Orange for hot
    if (score >= 40) return '#d97706'; // Yellow for warm
    if (score >= 20) return '#16a34a'; // Green for moderate
    return '#6b7280'; // Gray for low
  };

  const getTrendEmoji = (score: number): string => {
    if (score >= 80) return '🔥';
    if (score >= 60) return '📈';
    if (score >= 40) return '⬆️';
    if (score >= 20) return '↗️';
    return '📊';
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const getRankBadgeStyle = (rank: number) => {
    if (rank <= 3) {
      return {
        backgroundColor: '#fbbf24',
        color: '#78350f',
        border: '2px solid #f59e0b'
      };
    } else if (rank <= 10) {
      return {
        backgroundColor: '#6366f1',
        color: '#ffffff',
        border: '2px solid #4f46e5'
      };
    } else {
      return {
        backgroundColor: '#e5e7eb',
        color: '#6b7280',
        border: '2px solid #d1d5db'
      };
    }
  };

  return (
    <div
      style={{
        backgroundColor: '#fff',
        borderRadius: '12px',
        padding: '20px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb',
        transition: 'all 0.2s ease-in-out',
        cursor: onClick ? 'pointer' : 'default',
        position: 'relative',
        overflow: 'hidden'
      }}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        }
      }}
      onMouseLeave={(e) => {
        if (onClick) {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
        }
      }}
      onClick={() => onClick?.(topic)}
    >
      {/* Rank Badge */}
      <div
        style={{
          position: 'absolute',
          top: '16px',
          right: '16px',
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '14px',
          fontWeight: '700',
          ...getRankBadgeStyle(rank)
        }}
      >
        {rank}
      </div>

      {/* Topic Header */}
      <div style={{ marginBottom: '16px', paddingRight: '40px' }}>
        <h3 style={{
          fontSize: '20px',
          fontWeight: '600',
          color: '#1f2937',
          margin: '0 0 8px 0',
          lineHeight: '1.3'
        }}>
          {getTrendEmoji(topic.avg_trend_score)} {topic.topic_name}
        </h3>
        
        {/* Metadata Tags */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {topic.category && (
            <span style={{
              backgroundColor: '#f3f4f6',
              color: '#374151',
              padding: '4px 8px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: '500'
            }}>
              📂 {topic.category}
            </span>
          )}
          {topic.business && (
            <span style={{
              backgroundColor: '#eff6ff',
              color: '#1e40af',
              padding: '4px 8px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: '500'
            }}>
              🏢 {topic.business}
            </span>
          )}
          {topic.country_code && (
            <span style={{
              backgroundColor: '#f0fdf4',
              color: '#15803d',
              padding: '4px 8px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: '500'
            }}>
              🌍 {topic.country_code}
            </span>
          )}
        </div>
      </div>

      {/* Trend Score Section */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px',
        backgroundColor: '#f9fafb',
        borderRadius: '8px',
        marginBottom: '16px'
      }}>
        <div>
          <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
            Trend Score
          </div>
          <div style={{
            fontSize: '28px',
            fontWeight: '700',
            color: getTrendScoreColor(topic.avg_trend_score)
          }}>
            {topic.avg_trend_score.toFixed(1)}
          </div>
        </div>
        
        {topic.peak_trend_score && (
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
              Peak Score
            </div>
            <div style={{
              fontSize: '18px',
              fontWeight: '600',
              color: getTrendScoreColor(topic.peak_trend_score)
            }}>
              {topic.peak_trend_score.toFixed(1)}
            </div>
          </div>
        )}
      </div>

      {/* Statistics */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px'
      }}>
        {topic.total_volume && (
          <div>
            <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
              Total Volume
            </div>
            <div style={{ fontSize: '16px', fontWeight: '600', color: '#374151' }}>
              {formatNumber(topic.total_volume)}
            </div>
          </div>
        )}
        
        {topic.event_count && (
          <div>
            <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
              Events
            </div>
            <div style={{ fontSize: '16px', fontWeight: '600', color: '#374151' }}>
              {formatNumber(topic.event_count)}
            </div>
          </div>
        )}
      </div>

      {/* Trending Indicator */}
      <div style={{
        position: 'absolute',
        bottom: '0',
        left: '0',
        right: '0',
        height: '4px',
        background: `linear-gradient(90deg, ${getTrendScoreColor(topic.avg_trend_score)}, ${getTrendScoreColor(topic.avg_trend_score)}80)`,
        opacity: 0.8
      }} />
    </div>
  );
};

export default TrendCard;