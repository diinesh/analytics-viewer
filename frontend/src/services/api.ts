import axios from 'axios';
import { QueryRequest, QueryResponse, TrendingInsights, ComprehensiveAnalysis } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const queryAPI = {
  processQuery: async (query: string): Promise<QueryResponse> => {
    const request: QueryRequest = { query };
    const response = await api.post<QueryResponse>('/query', request);
    return response.data;
  },

  getTopicDetails: async (
    topicId: number, 
    timeRange: string = '7d', 
    statType: string = 'all', 
    country: string = 'all'
  ) => {
    const params = new URLSearchParams({
      time_range: timeRange,
      stat_type: statType,
      country: country
    });
    
    const response = await api.get(`/topic/${topicId}?${params}`);
    return response.data;
  },

  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // New trending analysis endpoints
  getTopicInsights: async (
    topicId: number, 
    timeRange: string = '24h'
  ): Promise<TrendingInsights> => {
    const params = new URLSearchParams({
      time_range: timeRange
    });
    
    const response = await api.get<TrendingInsights>(`/topic/${topicId}/insights?${params}`);
    return response.data;
  },

  getTopicAnalysis: async (
    topicId: number, 
    timeRange: string = '24h'
  ): Promise<ComprehensiveAnalysis> => {
    const params = new URLSearchParams({
      time_range: timeRange
    });
    
    const response = await api.get<ComprehensiveAnalysis>(`/topic/${topicId}/analysis?${params}`);
    return response.data;
  },
};

export default api;