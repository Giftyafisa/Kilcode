import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPaymentAdmin, setIsPaymentAdmin] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('admin_token');
    const adminType = localStorage.getItem('admin_type');
    if (token) {
      checkAuth(token, adminType);
    } else {
      setIsLoading(false);
    }
  }, []);

  const getBaseUrl = (isPaymentAdmin) => {
    return isPaymentAdmin 
      ? import.meta.env.VITE_PAYMENT_ADMIN_API_URL 
      : import.meta.env.VITE_MAIN_ADMIN_API_URL;
  };

  const checkAuth = async (token, adminType) => {
    try {
      const baseUrl = getBaseUrl(adminType === 'payment');
      const endpoint = adminType === 'payment'
        ? '/api/v1/payment-admin/auth/me'
        : '/api/v1/admin/auth/me';

      const response = await axios.get(`${baseUrl}${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setUser(response.data);
      setIsPaymentAdmin(adminType === 'payment');
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_type');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (registrationData) => {
    try {
      const isPaymentAdmin = registrationData.type === 'payment';
      const baseUrl = getBaseUrl(isPaymentAdmin);
      const endpoint = isPaymentAdmin
        ? '/api/v1/payment-admin/auth/register'
        : '/api/v1/admin/auth/register';

      console.log('Attempting registration at:', `${baseUrl}${endpoint}`);

      const response = await axios.post(`${baseUrl}${endpoint}`, registrationData);
      
      // If registration is successful, log in automatically
      if (response.data) {
        await login(registrationData.email, registrationData.password, endpoint);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Registration failed:', error);
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  };

  const login = async (email, password, endpoint) => {
    try {
      const isPaymentEndpoint = endpoint.includes('payment-admin');
      const baseUrl = getBaseUrl(isPaymentEndpoint);

      console.log('Attempting login to:', `${baseUrl}${endpoint}`);

      const response = await axios.post(`${baseUrl}${endpoint}`, {
        email,
        password
      });
      
      const { token, ...userData } = response.data;
      localStorage.setItem('admin_token', token);
      localStorage.setItem('admin_type', isPaymentEndpoint ? 'payment' : 'main');
      setUser(userData);
      setIsPaymentAdmin(isPaymentEndpoint);
      
      // Set default auth header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_type');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    setIsPaymentAdmin(false);
  };

  const value = {
    user,
    isLoading,
    isPaymentAdmin,
    register,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext; 