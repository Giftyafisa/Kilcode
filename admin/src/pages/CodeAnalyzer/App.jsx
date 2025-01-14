import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Dashboard from './Dashboard';
import CodeAnalyzerLogin from './Login';
import CodeAnalyzerLayout from '../../components/layout/CodeAnalyzerLayout';
import { useCodeAnalyzerAuth, CodeAnalyzerAuthProvider } from '../../context/CodeAnalyzerAuthContext';
import { Toaster } from 'react-hot-toast';
import AdminCodeUpload from './components/AdminCodeUpload';

// Dedicated protected route for code analyzer
const CodeAnalyzerProtectedRoute = ({ children }) => {
  const location = useLocation();
  const { user, isLoading } = useCodeAnalyzerAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    // Only redirect if we're not already on the login page
    if (location.pathname !== '/login') {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }
    return null;
  }

  // If we're on the login page but we're already authenticated, redirect to home
  if (location.pathname === '/login') {
    return <Navigate to="/" replace />;
  }

  return children;
};

// Login route component
const LoginRoute = () => {
  const { user, isLoading } = useCodeAnalyzerAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return <CodeAnalyzerLogin />;
};

// Main app component
const AppContent = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route
          path="/*"
          element={
            <CodeAnalyzerProtectedRoute>
              <CodeAnalyzerLayout>
                <Routes>
                  <Route index element={<Dashboard />} />
                  <Route path="upload" element={<AdminCodeUpload />} />
                </Routes>
              </CodeAnalyzerLayout>
            </CodeAnalyzerProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
};

// Wrapper component that provides all necessary providers
function App() {
  return (
    <BrowserRouter basename="/code-analyzer">
      <CodeAnalyzerAuthProvider>
        <Toaster 
          position="bottom-right"
          toastOptions={{
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
        <AppContent />
      </CodeAnalyzerAuthProvider>
    </BrowserRouter>
  );
}

export default App; 