/**
 * API Service
 * 
 * Centralized API client for backend communication.
 * Handles all HTTP requests to the FastAPI backend.
 */

import axios from 'axios';

// Base URL for API - uses environment variable or defaults to Render backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://stock-platform-r8yj.onrender.com';

const api = axios.create({
 baseURL: API_BASE_URL,
 headers: {
  'Content-Type': 'application/json',
 },
 timeout: 30000, // 30 second timeout
});

// Response interceptor for error handling
api.interceptors.response.use(
 response => response,
 error => {
  console.error('API Error:', error.response?.data || error.message);
  return Promise.reject(error);
 }
);

/**
 * Companies endpoints
 */
export const companiesApi = {
 getAll: () => api.get('/companies'),
 getOne: (symbol) => api.get(`/companies/${symbol}`),
};

/**
 * Stock data endpoints
 */
export const stockDataApi = {
 getData: (symbol, days = 30) => api.get(`/data/${symbol}`, { params: { days } }),
 getSummary: (symbol) => api.get(`/summary/${symbol}`),
};

/**
 * Comparison endpoints
 */
export const compareApi = {
 compare: (symbol1, symbol2) => api.get('/compare', { params: { symbol1, symbol2 } }),
 correlationMatrix: () => api.get('/compare/correlation-matrix'),
};

/**
 * Top movers endpoint
 */
export const topMoversApi = {
 get: () => api.get('/top-movers'),
};

/**
 * Predictions endpoints
 */
export const predictionsApi = {
 predict: (symbol, days = 7) => api.get(`/predict/${symbol}`, { params: { days } }),
 trainAll: () => api.post('/predict/train'),
 getStatus: (symbol) => api.get(`/predict/status/${symbol}`),
};

export default api;
