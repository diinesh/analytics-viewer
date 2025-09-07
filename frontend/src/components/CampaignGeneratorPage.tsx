import React, { useState, useEffect } from 'react';

interface CampaignGeneratorPageProps {
  topicId: number;
  topicName: string;
  onBack: () => void;
}

interface BrandProfile {
  brand_name: string;
  industry: string;
  business_vertical: string;
  brand_voice: string;
  target_markets: string[];
  core_values: string[];
  prohibited_topics: string[];
  website_url: string;
  logo_url: string;
}

interface AudienceProfile {
  demographics: {
    age_range: string;
    income: string;
    education: string;
  };
  interests: string[];
  pain_points: string[];
  preferred_platforms: string[];
  content_preferences: string[];
  geographic_focus: string[];
  age_range: string;
  income_level: string;
}

interface CampaignExamples {
  brand_examples: Array<{ name: string; profile: BrandProfile }>;
  audience_examples: Array<{ name: string; profile: AudienceProfile }>;
  campaign_goals: string[];
  channels: string[];
}

const CampaignGeneratorPage: React.FC<CampaignGeneratorPageProps> = ({
  topicId,
  topicName,
  onBack
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [examples, setExamples] = useState<CampaignExamples | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Campaign configuration state
  const [brandProfile, setBrandProfile] = useState<BrandProfile>({
    brand_name: '',
    industry: '',
    business_vertical: '',
    brand_voice: 'professional',
    target_markets: [],
    core_values: [],
    prohibited_topics: [],
    website_url: '',
    logo_url: ''
  });

  const [audienceProfile, setAudienceProfile] = useState<AudienceProfile>({
    demographics: { age_range: '', income: '', education: '' },
    interests: [],
    pain_points: [],
    preferred_platforms: [],
    content_preferences: [],
    geographic_focus: [],
    age_range: '',
    income_level: ''
  });

  const [campaignGoals, setCampaignGoals] = useState<string[]>([]);
  const [channels, setChannels] = useState<string[]>([]);
  const [budget, setBudget] = useState<number>(5000);
  const [duration, setDuration] = useState<number>(14);

  // Load examples on component mount
  useEffect(() => {
    const loadExamples = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/campaigns/examples');
        const data = await response.json();
        setExamples(data);
      } catch (err) {
        console.error('Failed to load examples:', err);
        setError('Failed to load campaign examples');
      }
    };
    
    loadExamples();
  }, []);

  const generateCampaign = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const campaignRequest = {
        topic_id: topicId,
        brand_profile: brandProfile,
        audience_profile: audienceProfile,
        campaign_goals: campaignGoals,
        channels: channels,
        budget: budget,
        duration_days: duration,
        urgent: false
      };

      const response = await fetch('http://localhost:8000/api/campaigns/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(campaignRequest)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Campaign generation failed');
      }

      const campaign = await response.json();
      setCurrentStep(5); // Results step
      // TODO: Store campaign results in state
      
    } catch (err) {
      console.error('Campaign generation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate campaign');
    } finally {
      setLoading(false);
    }
  };

  const renderStepIndicator = () => (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      marginBottom: '32px',
      gap: '16px'
    }}>
      {[1, 2, 3, 4].map((step) => (
        <div key={step} style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            backgroundColor: step <= currentStep ? '#3b82f6' : '#e5e7eb',
            color: step <= currentStep ? '#fff' : '#9ca3af',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: '600',
            fontSize: '14px'
          }}>
            {step}
          </div>
          {step < 4 && (
            <div style={{
              width: '40px',
              height: '2px',
              backgroundColor: step < currentStep ? '#3b82f6' : '#e5e7eb',
              marginLeft: '8px',
              marginRight: '8px'
            }} />
          )}
        </div>
      ))}
    </div>
  );

  const renderBrandProfileStep = () => (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '24px', textAlign: 'center' }}>
        Configure Your Brand Profile
      </h2>
      
      {examples && examples.brand_examples.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
            Quick Start Templates:
          </label>
          <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
            {examples.brand_examples.map((example, index) => (
              <button
                key={index}
                onClick={() => setBrandProfile(example.profile)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: '1px solid #d1d5db',
                  backgroundColor: '#f9fafb',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                {example.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gap: '16px' }}>
        <div>
          <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
            Brand Name*
          </label>
          <input
            type="text"
            value={brandProfile.brand_name}
            onChange={(e) => setBrandProfile({...brandProfile, brand_name: e.target.value})}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px'
            }}
            placeholder="Enter your brand name"
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
              Industry*
            </label>
            <input
              type="text"
              value={brandProfile.industry}
              onChange={(e) => setBrandProfile({...brandProfile, industry: e.target.value})}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px'
              }}
              placeholder="e.g. SaaS, Healthcare"
            />
          </div>

          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
              Brand Voice
            </label>
            <select
              value={brandProfile.brand_voice}
              onChange={(e) => setBrandProfile({...brandProfile, brand_voice: e.target.value})}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="authoritative">Authoritative</option>
              <option value="friendly">Friendly</option>
              <option value="witty">Witty</option>
            </select>
          </div>
        </div>

        <div>
          <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
            Website URL
          </label>
          <input
            type="url"
            value={brandProfile.website_url}
            onChange={(e) => setBrandProfile({...brandProfile, website_url: e.target.value})}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px'
            }}
            placeholder="https://yourwebsite.com"
          />
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
        <button
          onClick={onBack}
          style={{
            padding: '12px 24px',
            borderRadius: '8px',
            border: '1px solid #d1d5db',
            backgroundColor: '#f9fafb',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          ← Back to Analysis
        </button>
        
        <button
          onClick={() => setCurrentStep(2)}
          disabled={!brandProfile.brand_name || !brandProfile.industry}
          style={{
            padding: '12px 24px',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: (!brandProfile.brand_name || !brandProfile.industry) ? '#9ca3af' : '#3b82f6',
            color: '#fff',
            cursor: (!brandProfile.brand_name || !brandProfile.industry) ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          Next: Audience →
        </button>
      </div>
    </div>
  );

  const renderAudienceProfileStep = () => (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '24px', textAlign: 'center' }}>
        Define Your Target Audience
      </h2>
      
      {examples && examples.audience_examples.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
            Quick Start Templates:
          </label>
          <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
            {examples.audience_examples.map((example, index) => (
              <button
                key={index}
                onClick={() => setAudienceProfile(example.profile)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: '1px solid #d1d5db',
                  backgroundColor: '#f9fafb',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                {example.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gap: '16px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
              Age Range*
            </label>
            <input
              type="text"
              value={audienceProfile.age_range}
              onChange={(e) => setAudienceProfile({...audienceProfile, age_range: e.target.value})}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px'
              }}
              placeholder="e.g. 25-45"
            />
          </div>

          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
              Income Level
            </label>
            <input
              type="text"
              value={audienceProfile.income_level}
              onChange={(e) => setAudienceProfile({...audienceProfile, income_level: e.target.value})}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px'
              }}
              placeholder="e.g. 75k-150k"
            />
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
        <button
          onClick={() => setCurrentStep(1)}
          style={{
            padding: '12px 24px',
            borderRadius: '8px',
            border: '1px solid #d1d5db',
            backgroundColor: '#f9fafb',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          ← Back
        </button>
        
        <button
          onClick={() => setCurrentStep(3)}
          disabled={!audienceProfile.age_range}
          style={{
            padding: '12px 24px',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: !audienceProfile.age_range ? '#9ca3af' : '#3b82f6',
            color: '#fff',
            cursor: !audienceProfile.age_range ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          Next: Campaign →
        </button>
      </div>
    </div>
  );

  const renderCampaignConfigStep = () => (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '24px', textAlign: 'center' }}>
        Campaign Configuration
      </h2>

      <div style={{ display: 'grid', gap: '24px' }}>
        <div>
          <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '12px', display: 'block' }}>
            Campaign Goals*
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
            {examples?.campaign_goals.map((goal) => (
              <label key={goal} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={campaignGoals.includes(goal)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setCampaignGoals([...campaignGoals, goal]);
                    } else {
                      setCampaignGoals(campaignGoals.filter(g => g !== goal));
                    }
                  }}
                  style={{ marginRight: '8px' }}
                />
                <span style={{ fontSize: '14px', textTransform: 'capitalize' }}>
                  {goal.replace('_', ' ')}
                </span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '12px', display: 'block' }}>
            Marketing Channels*
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
            {examples?.channels.map((channel) => (
              <label key={channel} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={channels.includes(channel)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setChannels([...channels, channel]);
                    } else {
                      setChannels(channels.filter(c => c !== channel));
                    }
                  }}
                  style={{ marginRight: '8px' }}
                />
                <span style={{ fontSize: '14px', textTransform: 'capitalize' }}>
                  {channel}
                </span>
              </label>
            ))}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
              Budget ($)
            </label>
            <input
              type="number"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px'
              }}
              min="100"
              step="100"
            />
          </div>

          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
              Duration (days)
            </label>
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px'
              }}
              min="7"
              max="90"
            />
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
        <button
          onClick={() => setCurrentStep(2)}
          style={{
            padding: '12px 24px',
            borderRadius: '8px',
            border: '1px solid #d1d5db',
            backgroundColor: '#f9fafb',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          ← Back
        </button>
        
        <button
          onClick={generateCampaign}
          disabled={loading || campaignGoals.length === 0 || channels.length === 0}
          style={{
            padding: '12px 24px',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: (loading || campaignGoals.length === 0 || channels.length === 0) ? '#9ca3af' : '#10b981',
            color: '#fff',
            cursor: (loading || campaignGoals.length === 0 || channels.length === 0) ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          {loading ? 'Generating...' : '🚀 Generate Campaign'}
        </button>
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
          <h1 style={{ margin: 0, fontSize: '28px', fontWeight: 'bold', color: '#111827' }}>
            🚀 Marketing Campaign Generator
          </h1>
          <p style={{ margin: '8px 0 0 0', color: '#6b7280' }}>
            Creating campaign for: <strong>{topicName}</strong>
          </p>
        </div>
      </header>

      <div style={{ maxWidth: '800px', margin: '40px auto', padding: '0 20px' }}>
        {renderStepIndicator()}
        
        {error && (
          <div style={{
            backgroundColor: '#fee2e2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '24px',
            color: '#dc2626'
          }}>
            {error}
          </div>
        )}

        {currentStep === 1 && renderBrandProfileStep()}
        {currentStep === 2 && renderAudienceProfileStep()}
        {currentStep === 3 && renderCampaignConfigStep()}
        {currentStep === 4 && (
          <div style={{ textAlign: 'center' }}>
            <h2>Campaign Results</h2>
            <p>Campaign generation results will be displayed here...</p>
            <button onClick={onBack} style={{ padding: '12px 24px', marginTop: '20px' }}>
              Back to Topics
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CampaignGeneratorPage;