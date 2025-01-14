import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function AdminRoute({ children }) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  // Don't handle code analyzer routes
  if (location.pathname.startsWith('/code-analyzer')) {
    return children;
  }

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default AdminRoute; 