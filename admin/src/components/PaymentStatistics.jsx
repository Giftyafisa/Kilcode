import React from 'react';
import { useAuth } from '../context/AuthContext';

function PaymentStatistics({ statistics }) {
  const { user } = useAuth();
  const currencySymbol = user?.country?.toLowerCase() === 'nigeria' ? '₦' : 'GH₵';

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-gray-500 text-sm">Total Withdrawals</h3>
        <p className="text-2xl font-bold">{statistics.totalPayments}</p>
        <p className="text-sm text-gray-500">
          {currencySymbol}{statistics.totalAmount.toLocaleString()}
        </p>
      </div>
      
      <div className="bg-yellow-50 p-4 rounded-lg shadow">
        <h3 className="text-gray-500 text-sm">Pending</h3>
        <p className="text-2xl font-bold text-yellow-600">{statistics.pendingPayments}</p>
        <p className="text-sm text-gray-500">Awaiting verification</p>
      </div>
      
      <div className="bg-green-50 p-4 rounded-lg shadow">
        <h3 className="text-gray-500 text-sm">Approved</h3>
        <p className="text-2xl font-bold text-green-600">{statistics.approvedPayments}</p>
        <p className="text-sm text-gray-500">Successfully processed</p>
      </div>
      
      <div className="bg-red-50 p-4 rounded-lg shadow">
        <h3 className="text-gray-500 text-sm">Rejected</h3>
        <p className="text-2xl font-bold text-red-600">{statistics.rejectedPayments}</p>
        <p className="text-sm text-gray-500">Declined withdrawals</p>
      </div>
    </div>
  );
}

export default PaymentStatistics; 