import React, { createContext, useContext, useState, useEffect } from 'react';
import { codeAnalyzerService } from '../services/codeAnalyzerService';
import { toast } from 'react-hot-toast';

const CodeAnalyzerAuthContext = createContext(null);

export function CodeAnalyzerAuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [country, setCountry] = useState(localStorage.getItem('userCountry'));

  const handleError = (error) => {
    console.error('Auth Error:', error);
    let message;
    
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail;
      if (typeof detail === 'object' && !Array.isArray(detail)) {
        message = Object.values(detail).join(', ');
      } else if (Array.isArray(detail)) {
        message = detail.map(err => err.msg || err.message || String(err)).join(', ');
      } else {
        message = String(detail);
      }
    } else {
      message = error.message || String(error) || 'An unexpected error occurred';
    }
    
    toast.error(String(message));
  };

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('code_analyzer_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const userData = await codeAnalyzerService.verifyToken();
        setUser(userData);
        if (userData.country) {
          setCountry(userData.country.toLowerCase());
          localStorage.setItem('userCountry', userData.country.toLowerCase());
        }
      } catch (error) {
        console.error('Token verification failed:', error);
        handleError(error);
        localStorage.removeItem('code_analyzer_token');
        localStorage.removeItem('userCountry');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const userData = await codeAnalyzerService.login({ email, password });
      setUser(userData);
      if (userData.country) {
        setCountry(userData.country.toLowerCase());
        localStorage.setItem('userCountry', userData.country.toLowerCase());
      }
      toast.success('Login successful');
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      handleError(error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('code_analyzer_token');
    localStorage.removeItem('userCountry');
    setUser(null);
    setCountry(null);
    toast.success('Logged out successfully');
  };

  const value = {
    user,
    country,
    isLoading,
    login,
    logout,
    isCodeAnalyzer: true
  };

  return (
    <CodeAnalyzerAuthContext.Provider value={value}>
      {children}
    </CodeAnalyzerAuthContext.Provider>
  );
}

export function useCodeAnalyzerAuth() {
  const context = useContext(CodeAnalyzerAuthContext);
  if (!context) {
    throw new Error('useCodeAnalyzerAuth must be used within a CodeAnalyzerAuthProvider');
  }
  return context;
}

export default CodeAnalyzerAuthContext; 