import React, { useState } from 'react';
import QueryInput from './components/QueryInput';
import DataVisualization from './components/DataVisualization';
import SqlDisplay from './components/SqlDisplay';
import TrendingPage from './components/TrendingPage';
import TopicDetailPage from './components/TopicDetailPage';
import TrendingAnalysisPage from './components/TrendingAnalysisPage';
import CampaignGeneratorPage from './components/CampaignGeneratorPage';
import { queryAPI } from './services/api';
import { QueryResponse } from './types';
import './App.css';

type AppView = 'query' | 'trending' | 'topic-detail' | 'topic-analysis' | 'campaign-generator';

interface SelectedTopic {
  id: number;
  name: string;
}

function App() {
  const [currentView, setCurrentView] = useState<AppView>('trending');
  const [selectedTopic, setSelectedTopic] = useState<SelectedTopic | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (query: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await queryAPI.processQuery(query);
      setResult(response);
    } catch (err) {
      console.error('Query error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred while processing your query');
    } finally {
      setLoading(false);
    }
  };

  const handleTopicClick = (topicId: number, topicName: string) => {
    setSelectedTopic({ id: topicId, name: topicName });
    setCurrentView('topic-detail');
  };

  const handleViewAnalysis = (topicId: number, topicName: string) => {
    setSelectedTopic({ id: topicId, name: topicName });
    setCurrentView('topic-analysis');
  };

  const handleGenerateCampaign = (topicId: number, topicName: string) => {
    setSelectedTopic({ id: topicId, name: topicName });
    setCurrentView('campaign-generator');
  };

  const handleBackToTrending = () => {
    setCurrentView('trending');
    setSelectedTopic(null);
  };

  const handleBackToTopicDetail = () => {
    setCurrentView('topic-detail');
    // Keep selectedTopic as is
  };

  const handleBackToQuery = () => {
    setCurrentView('query');
    setSelectedTopic(null);
  };

  if (currentView === 'campaign-generator' && selectedTopic) {
    return (
      <CampaignGeneratorPage 
        topicId={selectedTopic.id}
        topicName={selectedTopic.name}
        onBack={handleBackToTrending}
      />
    );
  }

  if (currentView === 'topic-analysis' && selectedTopic) {
    return (
      <TrendingAnalysisPage 
        topicId={selectedTopic.id}
        topicName={selectedTopic.name}
        onBack={handleBackToTopicDetail}
        onGenerateCampaign={handleGenerateCampaign}
      />
    );
  }

  if (currentView === 'topic-detail' && selectedTopic) {
    return (
      <TopicDetailPage 
        topicId={selectedTopic.id}
        topicName={selectedTopic.name}
        onBack={handleBackToTrending}
        onViewAnalysis={handleViewAnalysis}
      />
    );
  }

  if (currentView === 'trending') {
    return (
      <TrendingPage 
        onNavigateToQuery={() => setCurrentView('query')}
        onTopicClick={handleTopicClick}
      />
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      <header style={{ 
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
                margin: 0 
              }}>
                Analytics Viewer
              </h1>
              <p style={{ 
                color: '#666', 
                margin: '8px 0 0 0',
                fontSize: '16px'
              }}>
                Ask questions about your data in natural language
              </p>
            </div>
            
            {/* Navigation */}
            <nav style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => setCurrentView('trending')}
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
                📈 Trending
              </button>
              <button
                onClick={() => setCurrentView('query')}
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
                🔍 Query
              </button>
            </nav>
          </div>
        </div>
      </header>

      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <QueryInput onSubmit={handleQuery} loading={loading} />
        
        {error && (
          <div style={{ 
            margin: '20px', 
            padding: '16px', 
            backgroundColor: '#fee', 
            border: '1px solid #fcc',
            borderRadius: '8px',
            color: '#c33'
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}
        
        {result && (
          <div>
            <SqlDisplay sql={result.sql} />
            <DataVisualization 
              data={result.data} 
              chartType={result.chart_type} 
              title={result.title} 
            />
          </div>
        )}
        
        {loading && (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px',
            color: '#666'
          }}>
            <div style={{ 
              display: 'inline-block',
              width: '32px',
              height: '32px',
              border: '3px solid #f3f3f3',
              borderTop: '3px solid #007bff',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
            <p style={{ marginTop: '16px' }}>Processing your query...</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
