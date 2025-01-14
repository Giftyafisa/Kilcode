import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCodeAnalyzerAuth } from '../context/CodeAnalyzerAuthContext';

const ProtectedRoute = ({ children, requireCodeAnalyzer = false }) => {
  const location = useLocation();
  const regularAuth = useAuth();
  const analyzerAuth = useCodeAnalyzerAuth();

  // Determine which auth context to use based on the route
  const isAnalyzerRoute = location.pathname.startsWith('/code-analyzer') || requireCodeAnalyzer;
  const auth = isAnalyzerRoute ? analyzerAuth : regularAuth;

  if (auth.isLoading) {
    return <div>Loading...</div>;
  }

  if (!auth.user) {
    // For code analyzer routes, redirect to code analyzer login
    if (isAnalyzerRoute) {
      return <Navigate to="/code-analyzer/login" state={{ from: location }} replace />;
    }
    // For admin routes, redirect to admin login
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  // For code analyzer routes, ensure the user is a code analyzer
  if (isAnalyzerRoute && !auth.isCodeAnalyzer) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

export default ProtectedRoute; 