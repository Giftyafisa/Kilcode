import React, { createContext, useContext, useState } from 'react';

const AdminContext = createContext(null);

export function AdminProvider({ children }) {
  const [adminState, setAdminState] = useState({
    payments: [],
    statistics: {
      pendingPayments: 0,
      processedToday: 0,
      totalVolume: 0
    }
  });

  const value = {
    adminState,
    setAdminState
  };

  return (
    <AdminContext.Provider value={value}>
      {children}
    </AdminContext.Provider>
  );
}

export function useAdmin() {
  const context = useContext(AdminContext);
  if (!context) {
    throw new Error('useAdmin must be used within an AdminProvider');
  }
  return context;
}

export default AdminContext; 