import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include session ID
api.interceptors.request.use((config) => {
  const sessionId = localStorage.getItem('sessionId') || generateSessionId();
  config.headers['X-Session-ID'] = sessionId;
  return config;
});

// Add response interceptor to handle session ID
api.interceptors.response.use((response) => {
  const sessionId = response.headers['x-session-id'];
  if (sessionId) {
    localStorage.setItem('sessionId', sessionId);
  }
  return response;
});

function generateSessionId() {
  const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
  localStorage.setItem('sessionId', sessionId);
  return sessionId;
}

// Agent API
export const agentAPI = {
  chat: async (message, sessionId = null) => {
    const response = await api.post('/agent/chat', {
      message,
      session_id: sessionId || localStorage.getItem('sessionId'),
    });
    return response.data;
  },

  getHistory: async (sessionId) => {
    const response = await api.get(`/agent/history/${sessionId}`);
    return response.data;
  },

  clearSession: async (sessionId) => {
    const response = await api.delete(`/agent/session/${sessionId}`);
    return response.data;
  },
};

// Bills API
export const billsAPI = {
  create: async (billData) => {
    const response = await api.post('/bills/', billData);
    return response.data;
  },

  getAll: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value);
      }
    });
    
    const response = await api.get(`/bills/?${params.toString()}`);
    return response.data;
  },

  getById: async (billId) => {
    const response = await api.get(`/bills/${billId}`);
    return response.data;
  },

  update: async (billId, billData) => {
    const response = await api.put(`/bills/${billId}`, billData);
    return response.data;
  },

  delete: async (billId) => {
    const response = await api.delete(`/bills/${billId}`);
    return response.data;
  },

  getUpcoming: async (days = 30) => {
    const response = await api.get(`/bills/upcoming/list?days=${days}`);
    return response.data;
  },

  getOverdue: async () => {
    const response = await api.get('/bills/overdue/list');
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  getSummary: async (year = null, month = null) => {
    const params = new URLSearchParams();
    if (year) params.append('year', year);
    if (month) params.append('month', month);
    
    const response = await api.get(`/analytics/summary?${params.toString()}`);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/analytics/stats');
    return response.data;
  },

  getCategoryAnalysis: async () => {
    const response = await api.get('/analytics/categories/analysis');
    return response.data;
  },

  getTrends: async (months = 6) => {
    const response = await api.get(`/analytics/trends?months=${months}`);
    return response.data;
  },
};

// Categories API
export const categoriesAPI = {
  getAll: async () => {
    const response = await api.get('/categories/');
    return response.data;
  },
};

export default api;