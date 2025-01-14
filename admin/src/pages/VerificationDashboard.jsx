import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import PaymentVerification from '../components/PaymentVerification';
import { toast } from 'react-hot-toast';
import axios from 'axios';

function VerificationDashboard() {
  const { user } = useAuth();
  const [pendingPayments, setPendingPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const ADMIN_API_URL = import.meta.env.VITE_ADMIN_API_URL;

  const VERIFICATION_STATES = {
    PENDING: 'pending',
    PROCESSING: 'processing',
    NEEDS_INFO: 'needs_info',
    VERIFIED: 'verified',
    REJECTED: 'rejected',
    CANCELLED: 'cancelled'
  };

  const fetchPendingVerifications = async () => {
    try {
      setLoading(true);
      // Get token from localStorage if not in user object
      const token = user?.token || localStorage.getItem('token');
      
      if (!token) {
        toast.error('Authentication token not found');
        return;
      }

      if (!user?.country) {
        toast.error('User country not found');
        return;
      }

      const response = await axios.get(
        `${ADMIN_API_URL}/api/v1/admin/verifications/pending?country=${user.country.toLowerCase()}`,
        {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data) {
        setPendingPayments(response.data);
      } else {
        setPendingPayments([]);
      }
    } catch (error) {
      console.error('Verification fetch error:', error);
      toast.error(error.response?.data?.detail || 'Failed to fetch pending verifications');
    } finally {
      setLoading(false);
    }
  };

  const handleVerificationUpdate = async (codeId, status, note = '') => {
    try {
      const token = user?.token || localStorage.getItem('token');
      
      if (!token) {
        toast.error('Authentication token not found');
        return;
      }

      await axios.post(
        `${ADMIN_API_URL}/api/v1/admin/verifications/${codeId}`,
        { 
          status,
          note,
          country: user.country.toLowerCase()
        },
        { 
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          } 
        }
      );
      
      toast.success('Verification status updated successfully');
      fetchPendingVerifications();
    } catch (error) {
      console.error('Verification update error:', error);
      toast.error(error.response?.data?.detail || 'Failed to update verification');
    }
  };

  // Use useEffect with proper dependency
  useEffect(() => {
    if (user?.country) {
      fetchPendingVerifications();
    }
  }, [user]); // Add user as dependency

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Verification Dashboard</h1>

      {/* Pending Payments Table */}
      <div className="bg-white rounded-lg shadow-md">
        <h2 className="text-xl font-semibold p-6 border-b">
          Pending Payment Verifications
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Payment Method
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {pendingPayments.map((payment) => (
                <tr key={payment.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {payment.user.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {payment.amount} {payment.currency}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {payment.method}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {new Date(payment.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <PaymentVerification
                      payment={payment}
                      onVerify={handleVerificationUpdate}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default VerificationDashboard; 