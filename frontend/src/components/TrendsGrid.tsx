import React from 'react';
import TrendCard from './TrendCard';

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

interface TrendsGridProps {
  trends: TrendingTopic[];
  loading?: boolean;
  error?: string | null;
  onTopicClick?: (topic: TrendingTopic) => void;
}

const TrendsGrid: React.FC<TrendsGridProps> = ({ 
  trends, 
  loading = false, 
  error = null,
  onTopicClick 
}) => {
  if (loading) {
    return (
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '12px',
        padding: '48px',
        textAlign: 'center',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <div style={{
          display: 'inline-block',
          width: '32px',
          height: '32px',
          border: '3px solid #f3f3f3',
          borderTop: '3px solid #3b82f6',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <p style={{ marginTop: '16px', color: '#666', fontSize: '16px' }}>
          Loading trending topics...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        backgroundColor: '#fef2f2',
        border: '1px solid #fecaca',
        borderRadius: '12px',
        padding: '24px',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
        <h3 style={{
          color: '#dc2626',
          fontSize: '18px',
          fontWeight: '600',
          marginBottom: '8px'
        }}>
          Error Loading Trends
        </h3>
        <p style={{ color: '#991b1b', fontSize: '14px', margin: 0 }}>
          {error}
        </p>
      </div>
    );
  }

  if (trends.length === 0) {
    return (
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '12px',
        padding: '48px',
        textAlign: 'center',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <div style={{ fontSize: '64px', marginBottom: '20px' }}>📈</div>
        <h3 style={{
          fontSize: '20px',
          fontWeight: '600',
          color: '#374151',
          marginBottom: '12px'
        }}>
          No Trending Topics Found
        </h3>
        <p style={{
          color: '#6b7280',
          fontSize: '16px',
          maxWidth: '500px',
          margin: '0 auto',
          lineHeight: '1.5'
        }}>
          No trending topics match your current filter criteria. Try adjusting your filters or selecting a different time range to discover what's trending.
        </p>
      </div>
    );
  }

  // Separate top 3 from the rest for special highlighting
  const topThree = trends.slice(0, 3);
  const remaining = trends.slice(3);

  return (
    <div>
      {/* Header with count */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '24px',
        padding: '0 4px'
      }}>
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#1f2937',
          margin: 0
        }}>
          Trending Now
        </h2>
        <div style={{
          backgroundColor: '#f3f4f6',
          color: '#374151',
          padding: '6px 12px',
          borderRadius: '20px',
          fontSize: '14px',
          fontWeight: '600'
        }}>
          {trends.length} topics
        </div>
      </div>

      {/* Top 3 - Featured Grid */}
      {topThree.length > 0 && (
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center'
          }}>
            🏆 Top Trending
          </h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '16px'
          }}>
            {topThree.map((topic, index) => (
              <TrendCard
                key={`top-${topic.topic_name}-${index}`}
                topic={topic}
                rank={index + 1}
                onClick={onTopicClick}
              />
            ))}
          </div>
        </div>
      )}

      {/* Remaining Topics - Compact Grid */}
      {remaining.length > 0 && (
        <div>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center'
          }}>
            📊 More Trending Topics
          </h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '16px'
          }}>
            {remaining.map((topic, index) => (
              <TrendCard
                key={`remaining-${topic.topic_name}-${index}`}
                topic={topic}
                rank={index + 4}
                onClick={onTopicClick}
              />
            ))}
          </div>
        </div>
      )}

      {/* Trending Summary */}
      {trends.length > 0 && (
        <div style={{
          backgroundColor: '#f9fafb',
          borderRadius: '12px',
          padding: '20px',
          marginTop: '32px',
          textAlign: 'center'
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '20px',
            maxWidth: '600px',
            margin: '0 auto'
          }}>
            <div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#dc2626',
                marginBottom: '4px'
              }}>
                {Math.max(...trends.map(t => t.avg_trend_score)).toFixed(1)}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>
                Highest Score
              </div>
            </div>
            
            <div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#059669',
                marginBottom: '4px'
              }}>
                {(trends.reduce((sum, t) => sum + t.avg_trend_score, 0) / trends.length).toFixed(1)}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>
                Average Score
              </div>
            </div>
            
            {trends.some(t => t.total_volume) && (
              <div>
                <div style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#7c3aed',
                  marginBottom: '4px'
                }}>
                  {(() => {
                    const totalVolume = trends
                      .filter(t => t.total_volume)
                      .reduce((sum, t) => sum + (t.total_volume || 0), 0);
                    return totalVolume >= 1000000 
                      ? `${(totalVolume / 1000000).toFixed(1)}M`
                      : totalVolume >= 1000
                      ? `${(totalVolume / 1000).toFixed(1)}K`
                      : totalVolume.toString();
                  })()}
                </div>
                <div style={{ fontSize: '12px', color: '#6b7280' }}>
                  Total Volume
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TrendsGrid;