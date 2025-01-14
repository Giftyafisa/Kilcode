import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AdminProvider } from './context/AdminContext';
import PaymentAdminApp from './PaymentAdminApp';
import axios from 'axios';
import './index.css';

// Configure axios defaults
axios.defaults.baseURL = import.meta.env.VITE_ADMIN_API_URL || 'http://localhost:8002';

// Ensure the root element exists
const rootElement = document.getElementById('root');
if (!rootElement) {
  const root = document.createElement('div');
  root.id = 'root';
  document.body.appendChild(root);
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter basename="/payment-admin">
      <AuthProvider>
        <AdminProvider>
          <PaymentAdminApp />
        </AdminProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
); 