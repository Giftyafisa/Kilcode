import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { AdminProvider } from './context/AdminContext';
import { BettingProvider } from './context/BettingContext';
import { ChatProvider } from './context/ChatContext';
import AdminLogin from './pages/AdminLogin';
import AdminRegister from './pages/AdminRegister';
import AdminDashboard from './pages/AdminDashboard';
import UsersManagement from './pages/UsersManagement';
import AdminRoute from './components/AdminRoute';
import AdminNavbar from './components/AdminNavbar';
import BettingCodesDashboard from './pages/BettingCodesDashboard';
import { useAuth } from './context/AuthContext';

// Layout component for protected routes
const AdminLayout = () => {
  const { user } = useAuth();
  
  if (!user) return null;
  
  return (
    <>
      <AdminNavbar />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route index element={<AdminDashboard />} />
          <Route path="users" element={<UsersManagement />} />
          <Route path="betting-codes" element={<BettingCodesDashboard />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  );
};

function App() {
  // Check if we're on the code analyzer route
  if (window.location.pathname.startsWith('/code-analyzer')) {
    return null;
  }

  return (
    <Router>
      <AuthProvider>
        <AdminProvider>
          <BettingProvider>
            <ChatProvider>
              <div className="min-h-screen bg-gray-100">
                <Routes>
                  {/* Public Routes */}
                  <Route path="/login" element={<AdminLogin />} />
                  <Route path="/register" element={<AdminRegister />} />
                  
                  {/* Protected Routes */}
                  <Route
                    path="/*"
                    element={
                      <AdminRoute>
                        <AdminLayout />
                      </AdminRoute>
                    }
                  />
                </Routes>
                <Toaster position="top-right" />
              </div>
            </ChatProvider>
          </BettingProvider>
        </AdminProvider>
      </AuthProvider>
    </Router>
  );
}

export default App; 