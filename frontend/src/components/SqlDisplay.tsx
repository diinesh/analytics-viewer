import React, { useState } from 'react';
import { Code, Copy, Check } from 'lucide-react';

interface SqlDisplayProps {
  sql: string;
}

const SqlDisplay: React.FC<SqlDisplayProps> = ({ sql }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy SQL:', err);
    }
  };

  return (
    <div style={{ margin: '20px', border: '1px solid #e0e0e0', borderRadius: '8px' }}>
      <div 
        style={{ 
          padding: '12px 16px', 
          backgroundColor: '#f5f5f5', 
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer'
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Code size={16} />
          <span style={{ fontWeight: 'bold' }}>Generated SQL</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleCopy();
            }}
            style={{
              padding: '4px 8px',
              backgroundColor: 'transparent',
              border: '1px solid #ccc',
              borderRadius: '4px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? 'Copied!' : 'Copy'}
          </button>
          <span style={{ fontSize: '12px' }}>
            {isExpanded ? '▼' : '▶'}
          </span>
        </div>
      </div>
      
      {isExpanded && (
        <div style={{ padding: '16px' }}>
          <pre style={{ 
            backgroundColor: '#f8f9fa', 
            padding: '12px', 
            borderRadius: '4px', 
            overflow: 'auto',
            fontSize: '14px',
            fontFamily: 'monospace',
            margin: 0,
            whiteSpace: 'pre-wrap'
          }}>
            {sql}
          </pre>
        </div>
      )}
    </div>
  );
};

export default SqlDisplay;