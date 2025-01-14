import React from 'react';
import { useAdmin } from '../context/AdminContext';

function VerificationFilters() {
  const { state, setFilters } = useAdmin();
  const { filters } = state;

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Date Range</label>
          <select
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            value={filters.dateRange}
            onChange={(e) => setFilters({ dateRange: e.target.value })}
          >
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="custom">Custom Range</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Status</label>
          <select
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            value={filters.status}
            onChange={(e) => setFilters({ status: e.target.value })}
          >
            <option value="all">All</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Type</label>
          <select
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            value={filters.type}
            onChange={(e) => setFilters({ type: e.target.value })}
          >
            <option value="all">All Types</option>
            <option value="payment">Payments</option>
            <option value="user">Users</option>
            <option value="code">Codes</option>
          </select>
        </div>
      </div>
    </div>
  );
}

export default VerificationFilters; 