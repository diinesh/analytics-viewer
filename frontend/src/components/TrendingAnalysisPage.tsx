import React, { useState, useEffect } from 'react';
import { ComprehensiveAnalysis } from '../types';
import { queryAPI } from '../services/api';

interface TrendingAnalysisPageProps {
  topicId: number;
  topicName: string;
  onBack: () => void;
  timeRange?: string;
}

const TrendingAnalysisPage: React.FC<TrendingAnalysisPageProps> = ({
  topicId,
  topicName,
  onBack,
  timeRange = '24h'
}) => {
  const [analysis, setAnalysis] = useState<ComprehensiveAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const data = await queryAPI.getTopicAnalysis(topicId, timeRange);
        setAnalysis(data);
      } catch (err) {
        console.error('Error fetching analysis:', err);
        setError(err instanceof Error ? err.message : 'Failed to load analysis');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [topicId, timeRange]);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
        <header style={{ 
          backgroundColor: '#fff', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          padding: '20px 0' 
        }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
            <button
              onClick={onBack}
              style={{
                backgroundColor: '#f3f4f6',
                border: 'none',
                borderRadius: '8px',
                padding: '10px 16px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                marginBottom: '16px'
              }}
            >
              ← Back
            </button>
            <h1 style={{ margin: 0, fontSize: '28px', fontWeight: 'bold', color: '#111827' }}>
              🔍 Trending Analysis: {topicName}
            </h1>
          </div>
        </header>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '400px',
          color: '#666'
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
          <span style={{ marginLeft: '16px', fontSize: '18px' }}>Analyzing trending patterns...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
        <header style={{ 
          backgroundColor: '#fff', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          padding: '20px 0' 
        }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
            <button
              onClick={onBack}
              style={{
                backgroundColor: '#f3f4f6',
                border: 'none',
                borderRadius: '8px',
                padding: '10px 16px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                marginBottom: '16px'
              }}
            >
              ← Back
            </button>
            <h1 style={{ margin: 0, fontSize: '28px', fontWeight: 'bold', color: '#111827' }}>
              🔍 Trending Analysis: {topicName}
            </h1>
          </div>
        </header>

        <div style={{
          maxWidth: '1200px',
          margin: '40px auto',
          padding: '0 20px'
        }}>
          <div style={{
            backgroundColor: '#fee2e2',
            border: '1px solid #fecaca',
            borderRadius: '12px',
            padding: '24px',
            textAlign: 'center'
          }}>
            <h3 style={{ margin: '0 0 16px 0', color: '#dc2626' }}>Analysis Unavailable</h3>
            <p style={{ margin: 0, color: '#7f1d1d' }}>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return null;
  }

  const CardContainer: React.FC<{ children: React.ReactNode; title: string; icon: string }> = ({ children, title, icon }) => (
    <div style={{
      backgroundColor: '#fff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      margin: '16px 0',
      border: '1px solid #e5e7eb'
    }}>
      <h3 style={{
        margin: '0 0 20px 0',
        fontSize: '18px',
        fontWeight: '600',
        color: '#111827',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        {icon} {title}
      </h3>
      {children}
    </div>
  );

  const InfoItem: React.FC<{ label: string; value: string; color?: string }> = ({ label, value, color = '#4b5563' }) => (
    <div style={{ marginBottom: '12px' }}>
      <div style={{
        fontSize: '13px',
        fontWeight: '600',
        color: '#6b7280',
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
        marginBottom: '4px'
      }}>
        {label}
      </div>
      <div style={{
        fontSize: '14px',
        lineHeight: '1.5',
        color: color,
        whiteSpace: 'pre-wrap'
      }}>
        {value}
      </div>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      {/* Header */}
      <header style={{ 
        backgroundColor: '#fff', 
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        padding: '20px 0' 
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <button
            onClick={onBack}
            style={{
              backgroundColor: '#f3f4f6',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 16px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              marginBottom: '16px',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#e5e7eb';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = '#f3f4f6';
            }}
          >
            ← Back to Topic Details
          </button>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start'
          }}>
            <div>
              <h1 style={{ margin: '0 0 8px 0', fontSize: '28px', fontWeight: 'bold', color: '#111827' }}>
                🔍 Trending Analysis: {analysis.topic_info.topic_name}
              </h1>
              <div style={{
                display: 'flex',
                gap: '12px',
                alignItems: 'center'
              }}>
                <span style={{
                  backgroundColor: '#dbeafe',
                  color: '#1e40af',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '13px',
                  fontWeight: '500'
                }}>
                  {analysis.topic_info.category}
                </span>
                <span style={{
                  backgroundColor: '#dcfce7',
                  color: '#166534',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '13px',
                  fontWeight: '500'
                }}>
                  {analysis.topic_info.business}
                </span>
              </div>
            </div>
            <div style={{
              textAlign: 'right',
              fontSize: '12px',
              color: '#6b7280'
            }}>
              Analysis generated on<br/>
              {new Date(analysis.topic_info.analysis_timestamp).toLocaleString()}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '20px'
      }}>
        {/* Trending Reason */}
        <CardContainer title="Why It's Trending" icon="🔥">
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '20px'
          }}>
            <InfoItem 
              label="Primary Cause" 
              value={analysis.trending_analysis.trending_reason.primary_cause} 
              color="#111827"
            />
            <InfoItem 
              label="Specific Event" 
              value={analysis.trending_analysis.trending_reason.specific_event}
            />
            <InfoItem 
              label="Timing Factor" 
              value={analysis.trending_analysis.trending_reason.timing_factor}
            />
          </div>
        </CardContainer>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '20px'
        }}>
          {/* Content Analysis */}
          <CardContainer title="Content Analysis" icon="📰">
            <InfoItem 
              label="Content Type" 
              value={analysis.trending_analysis.content_analysis.content_type}
            />
            <InfoItem 
              label="Story Summary" 
              value={analysis.trending_analysis.content_analysis.story_summary}
            />
            <div style={{ marginBottom: '12px' }}>
              <div style={{
                fontSize: '13px',
                fontWeight: '600',
                color: '#6b7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px'
              }}>
                Key Drivers
              </div>
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '6px'
              }}>
                {analysis.trending_analysis.content_analysis.key_drivers.map((driver, index) => (
                  <span
                    key={index}
                    style={{
                      backgroundColor: '#fef3c7',
                      color: '#92400e',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: '500'
                    }}
                  >
                    {driver}
                  </span>
                ))}
              </div>
            </div>
          </CardContainer>

          {/* Trend Patterns */}
          <CardContainer title="Trend Patterns" icon="📈">
            <InfoItem 
              label="Velocity" 
              value={analysis.trending_analysis.trend_patterns.velocity}
            />
            <InfoItem 
              label="Momentum" 
              value={analysis.trending_analysis.trend_patterns.momentum}
            />
            <InfoItem 
              label="Geographic Insight" 
              value={analysis.trending_analysis.trend_patterns.geographic_insight}
            />
            <InfoItem 
              label="Demographic Appeal" 
              value={analysis.trending_analysis.trend_patterns.demographic_appeal}
            />
          </CardContainer>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '20px'
        }}>
          {/* Business Context */}
          <CardContainer title="Business Context" icon="💼">
            <InfoItem 
              label="Category Fit" 
              value={analysis.trending_analysis.business_context.category_fit}
            />
            <InfoItem 
              label="Business Relevance" 
              value={analysis.trending_analysis.business_context.business_relevance}
            />
            <InfoItem 
              label="Market Impact" 
              value={analysis.trending_analysis.business_context.market_impact}
            />
          </CardContainer>

          {/* Predictions */}
          <CardContainer title="Trend Predictions" icon="🔮">
            <InfoItem 
              label="Trend Duration" 
              value={analysis.trending_analysis.prediction.trend_duration}
            />
            <InfoItem 
              label="Peak Prediction" 
              value={analysis.trending_analysis.prediction.peak_prediction}
            />
            <InfoItem 
              label="Related Trends" 
              value={analysis.trending_analysis.prediction.related_trends}
            />
          </CardContainer>
        </div>

        {/* Web Context */}
        {analysis.web_context && (
          <CardContainer title="Web Search Context" icon="🌐">
            <InfoItem 
              label="Search Query Used" 
              value={analysis.web_context.search_query}
            />
            <InfoItem 
              label="Content Summary" 
              value={analysis.web_context.content_summary}
            />
            {analysis.web_context.key_themes && analysis.web_context.key_themes.length > 0 && (
              <div>
                <div style={{
                  fontSize: '13px',
                  fontWeight: '600',
                  color: '#6b7280',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  marginBottom: '8px'
                }}>
                  Web Themes
                </div>
                <div style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '6px'
                }}>
                  {analysis.web_context.key_themes.map((theme, index) => (
                    <span
                      key={index}
                      style={{
                        backgroundColor: '#e0e7ff',
                        color: '#3730a3',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: '500'
                      }}
                    >
                      {theme}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContainer>
        )}
      </div>
    </div>
  );
};

export default TrendingAnalysisPage;