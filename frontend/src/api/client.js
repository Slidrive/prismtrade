import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const authAPI = {
  register: (data) => apiClient.post('/api/auth/register', data),
  login: (data) => apiClient.post('/api/auth/login', data),
  getMe: () => apiClient.get('/api/auth/me'),
};

export const strategyAPI = {
  getAll: () => apiClient.get('/api/strategies'),
  getOne: (id) => apiClient.get(`/api/strategies/${id}`),
  create: (data) => apiClient.post('/api/strategies', data),
  update: (id, data) => apiClient.put(`/api/strategies/${id}`, data),
  delete: (id) => apiClient.delete(`/api/strategies/${id}`),
  start: (id) => apiClient.post(`/api/strategies/${id}/start`),
  stop: (id) => apiClient.post(`/api/strategies/${id}/stop`),
};

export const backtestAPI = {
  run: (strategyId, data) => apiClient.post(`/api/strategies/${strategyId}/backtest`, data),
  getResults: (strategyId) => apiClient.get(`/api/strategies/${strategyId}/backtests`),
};

export const tradeAPI = {
  getAll: (params) => apiClient.get('/api/trades', { params }),
  getForStrategy: (strategyId) => apiClient.get(`/api/strategies/${strategyId}/trades`),
};

export default apiClient;
