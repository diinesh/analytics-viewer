import React, { useState } from 'react';
import { Send } from 'lucide-react';

interface QueryInputProps {
  onSubmit: (query: string) => void;
  loading: boolean;
}

const QueryInput: React.FC<QueryInputProps> = ({ onSubmit, loading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSubmit(query.trim());
    }
  };

  return (
    <div style={{ padding: '20px', borderBottom: '1px solid #e0e0e0' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything about your data... (e.g., 'Show me sales trends over time')"
          style={{
            flex: 1,
            padding: '12px 16px',
            border: '2px solid #e0e0e0',
            borderRadius: '8px',
            fontSize: '16px',
            outline: 'none',
          }}
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          style={{
            padding: '12px 20px',
            backgroundColor: loading || !query.trim() ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <Send size={16} />
          {loading ? 'Processing...' : 'Query'}
        </button>
      </form>
    </div>
  );
};

export default QueryInput;