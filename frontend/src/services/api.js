import axios from 'axios';

// Use relative URL to leverage Vite's proxy
const API_BASE_URL = '/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add request interceptor to include session ID
api.interceptors.request.use((config) => {
  const sessionId = localStorage.getItem('sessionId') || generateSessionId();
  config.headers['X-Session-ID'] = sessionId;
  return config;
}, (error) => {
  console.error('Request interceptor error:', error);
  return Promise.reject(error);
});

// Add response interceptor to handle session ID and errors
api.interceptors.response.use((response) => {
  const sessionId = response.headers['x-session-id'];
  if (sessionId) {
    localStorage.setItem('sessionId', sessionId);
  }
  return response;
}, (error) => {
  console.error('API Error:', error);
  
  if (error.code === 'ECONNABORTED') {
    console.error('Request timeout');
  } else if (error.response?.status === 500) {
    console.error('Server error');
  } else if (error.response?.status === 404) {
    console.error('Endpoint not found');
  }
  
  return Promise.reject(error);
});

function generateSessionId() {
  const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
  localStorage.setItem('sessionId', sessionId);
  return sessionId;
}

// Agent API
export const agentAPI = {
  chat: async (message, sessionId = null) => {
    try {
      const response = await api.post('/agent/chat', {
        message,
        session_id: sessionId || localStorage.getItem('sessionId'),
      });
      return response.data;
    } catch (error) {
      console.error('Chat API error:', error);
      throw error;
    }
  },

  getHistory: async (sessionId) => {
    try {
      const response = await api.get(`/agent/history/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('History API error:', error);
      throw error;
    }
  },

  clearSession: async (sessionId) => {
    try {
      const response = await api.delete(`/agent/session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Clear session API error:', error);
      throw error;
    }
  },
};

// Bills API
export const billsAPI = {
  create: async (billData) => {
    try {
      const response = await api.post('/bills/', billData);
      return response.data;
    } catch (error) {
      console.error('Create bill API error:', error);
      throw error;
    }
  },

  getAll: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/bills/?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Get bills API error:', error);
      throw error;
    }
  },

  getById: async (billId) => {
    try {
      const response = await api.get(`/bills/${billId}`);
      return response.data;
    } catch (error) {
      console.error('Get bill by ID API error:', error);
      throw error;
    }
  },

  update: async (billId, billData) => {
    try {
      const response = await api.put(`/bills/${billId}`, billData);
      return response.data;
    } catch (error) {
      console.error('Update bill API error:', error);
      throw error;
    }
  },

  delete: async (billId) => {
    try {
      const response = await api.delete(`/bills/${billId}`);
      return response.data;
    } catch (error) {
      console.error('Delete bill API error:', error);
      throw error;
    }
  },

  getUpcoming: async (days = 30) => {
    try {
      const response = await api.get(`/bills/upcoming/list?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Get upcoming bills API error:', error);
      throw error;
    }
  },

  getOverdue: async () => {
    try {
      const response = await api.get('/bills/overdue/list');
      return response.data;
    } catch (error) {
      console.error('Get overdue bills API error:', error);
      throw error;
    }
  },
};

// Analytics API
export const analyticsAPI = {
  getSummary: async (year = null, month = null) => {
    try {
      const params = new URLSearchParams();
      if (year) params.append('year', year);
      if (month) params.append('month', month);
      
      const response = await api.get(`/analytics/summary?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Get summary API error:', error);
      throw error;
    }
  },

  getStats: async () => {
    try {
      const response = await api.get('/analytics/stats');
      return response.data;
    } catch (error) {
      console.error('Get stats API error:', error);
      throw error;
    }
  },

  getCategoryAnalysis: async () => {
    try {
      const response = await api.get('/analytics/categories/analysis');
      return response.data;
    } catch (error) {
      console.error('Get category analysis API error:', error);
      throw error;
    }
  },

  getTrends: async (months = 6) => {
    try {
      const response = await api.get(`/analytics/trends?months=${months}`);
      return response.data;
    } catch (error) {
      console.error('Get trends API error:', error);
      throw error;
    }
  },
};

// Categories API
export const categoriesAPI = {
  getAll: async () => {
    try {
      const response = await api.get('/categories/');
      return response.data;
    } catch (error) {
      console.error('Get categories API error:', error);
      throw error;
    }
  },
};

export default api;