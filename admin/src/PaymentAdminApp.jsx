import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import AdminLogin from './pages/AdminLogin';
import PaymentAdminDashboard from './pages/PaymentAdminDashboard';
import AdminRoute from './components/AdminRoute';
import PaymentAdminNavbar from './components/PaymentAdminNavbar';
import { useAuth } from './context/AuthContext';

// Layout component for protected routes
const PaymentAdminLayout = () => {
  const { user } = useAuth();
  
  if (!user) return null;
  
  return (
    <>
      <PaymentAdminNavbar />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route index element={<PaymentAdminDashboard />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  );
};

function PaymentAdminApp() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<AdminLogin />} />
        
        {/* Protected Routes */}
        <Route
          path="/*"
          element={
            <AdminRoute>
              <PaymentAdminLayout />
            </AdminRoute>
          }
        />
      </Routes>
      <Toaster position="top-right" />
    </div>
  );
}

export default PaymentAdminApp; 