import axios from 'axios';
import { toast } from 'react-hot-toast';

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_CODE_ANALYZER_API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Get token and country from localStorage
    const token = localStorage.getItem('code_analyzer_token');
    const country = localStorage.getItem('userCountry')?.toLowerCase() || 
                   JSON.parse(localStorage.getItem('user') || '{}')?.country?.toLowerCase();

    // Add auth token if available
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add country header if available
    if (country) {
      config.headers['X-Country'] = country;
    }

    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Clear token and redirect to login
      localStorage.removeItem('code_analyzer_token');
      window.location.href = '/code-analyzer/login';
      
      return Promise.reject(error);
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      toast.error('You do not have permission to perform this action');
      return Promise.reject(error);
    }

    // Handle 404 Not Found
    if (error.response?.status === 404) {
      toast.error('The requested resource was not found');
      return Promise.reject(error);
    }

    // Handle 422 Validation Error
    if (error.response?.status === 422) {
      let message;
      const detail = error.response.data?.detail;
      
      if (typeof detail === 'object' && !Array.isArray(detail)) {
        message = Object.values(detail).join(', ');
      } else if (Array.isArray(detail)) {
        message = detail.map(err => err.msg || err.message || String(err)).join(', ');
      } else {
        message = String(detail || 'Validation error occurred');
      }
      
      toast.error(message);
      return Promise.reject(error);
    }

    // Handle 429 Too Many Requests
    if (error.response?.status === 429) {
      toast.error('Too many requests. Please try again later');
      return Promise.reject(error);
    }

    // Handle network errors
    if (!error.response) {
      toast.error('Network error. Please check your connection');
      return Promise.reject(error);
    }

    // Handle other errors
    let message;
    const detail = error.response?.data?.detail;
    
    if (typeof detail === 'object' && !Array.isArray(detail)) {
      message = Object.values(detail).join(', ');
    } else if (Array.isArray(detail)) {
      message = detail.map(err => err.msg || err.message || String(err)).join(', ');
    } else {
      message = String(detail || error.message || 'An unexpected error occurred');
    }
    
    toast.error(message);
    return Promise.reject(error);
  }
);

export default api; 