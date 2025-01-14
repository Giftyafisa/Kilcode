import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import CodeVerification from '../components/CodeVerification';

function AdminDashboard() {
  const { user } = useAuth();
  const [pendingCodes, setPendingCodes] = useState([]);
  const [statistics, setStatistics] = useState({
    users: { total: 0 },
    betting: {
      total_codes: 0,
      pending_codes: 0,
      won_codes: 0,
      lost_codes: 0
    }
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const API_URL = import.meta.env.VITE_MAIN_ADMIN_API_URL;

  useEffect(() => {
    if (user?.country) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      if (!token) {
        toast.error('No authentication token found');
        return;
      }

      console.log('Using token:', token);

      const headers = { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const [statsRes, codesRes] = await Promise.all([
        axios.get(`${API_URL}/api/v1/admin/dashboard/statistics`, { headers }),
        axios.get(`${API_URL}/api/v1/admin/dashboard/pending-verifications`, { headers })
      ]);

      if (statsRes.data) {
        setStatistics({
          users: { total: statsRes.data.users?.total || 0 },
          betting: {
            total_codes: statsRes.data.betting?.total_codes || 0,
            pending_codes: statsRes.data.betting?.pending_codes || 0,
            won_codes: statsRes.data.betting?.won_codes || 0,
            lost_codes: statsRes.data.betting?.lost_codes || 0
          }
        });
      }

      if (Array.isArray(codesRes.data)) {
        setPendingCodes(codesRes.data);
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      console.log('Error response:', error.response);
      const errorMessage = error.response?.data?.detail || 'Failed to fetch dashboard data';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCodeVerification = async (codeId, status) => {
    try {
      const token = localStorage.getItem('admin_token');
      const headers = { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      await axios.post(
        `${API_URL}/api/v1/admin/dashboard/verify-code/${codeId}`, 
        { status },
        { headers }
      );
      
      setPendingCodes(codes => codes.filter(code => code.id !== codeId));
      toast.success('Code verified successfully');
      fetchDashboardData();
    } catch (error) {
      console.error('Error verifying code:', error.response || error);
      toast.error(error.response?.data?.detail || 'Failed to verify code');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">
        {user?.country?.charAt(0).toUpperCase() + user?.country?.slice(1)} Admin Dashboard
      </h1>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-2">Total Users</h3>
          <p className="text-3xl font-bold text-blue-600">{statistics?.users?.total || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-2">Total Codes</h3>
          <p className="text-3xl font-bold text-green-600">{statistics?.betting?.total_codes || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-2">Won Codes</h3>
          <p className="text-3xl font-bold text-green-600">{statistics?.betting?.won_codes || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-2">Lost Codes</h3>
          <p className="text-3xl font-bold text-red-600">{statistics?.betting?.lost_codes || 0}</p>
        </div>
      </div>

      {/* Pending Codes Table */}
      <div className="bg-white rounded-lg shadow-md">
        <h2 className="text-xl font-semibold p-6 border-b">Pending Verifications</h2>
        {pendingCodes.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            No pending verifications
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bookmaker</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Odds</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stake</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Potential Win</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Submitted</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {pendingCodes.map((code) => (
                  <tr key={code.id}>
                    <td className="px-6 py-4 whitespace-nowrap">{code.user_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{code.code}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{code.bookmaker}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{code.odds}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{code.stake}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{code.potential_winnings}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {new Date(code.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <CodeVerification 
                        code={code} 
                        onVerify={(status) => handleCodeVerification(code.id, status)} 
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminDashboard; 