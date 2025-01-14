import React from 'react';
import { useAuth } from '../context/AuthContext';

function CountryStatistics({ statistics }) {
  const { user } = useAuth();
  const currencySymbol = user?.country === 'nigeria' ? '₦' : 'GH₵';

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-2">Booking Codes</h3>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Pending</span>
            <span className="font-bold text-yellow-600">{statistics.pendingCodes}</span>
          </div>
          <div className="flex justify-between">
            <span>Won</span>
            <span className="font-bold text-green-600">{statistics.wonCodes}</span>
          </div>
          <div className="flex justify-between">
            <span>Lost</span>
            <span className="font-bold text-red-600">{statistics.lostCodes}</span>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-2">Withdrawals</h3>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Pending</span>
            <span className="font-bold text-yellow-600">{statistics.pendingWithdrawals}</span>
          </div>
          <div className="flex justify-between">
            <span>Amount</span>
            <span className="font-bold">{currencySymbol}{statistics.withdrawalAmount?.toLocaleString()}</span>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-2">Country Stats</h3>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Total Users</span>
            <span className="font-bold">{statistics.totalUsers}</span>
          </div>
          <div className="flex justify-between">
            <span>Active Users</span>
            <span className="font-bold text-green-600">{statistics.activeUsers}</span>
          </div>
          <div className="flex justify-between">
            <span>Total Revenue</span>
            <span className="font-bold text-blue-600">{currencySymbol}{statistics.totalRevenue?.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CountryStatistics; 