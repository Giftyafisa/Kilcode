import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useAdmin } from '../context/AdminContext';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import PaymentStatistics from '../components/PaymentStatistics';

function PaymentsManagement() {
  const { user } = useAuth();
  const { state, updateVerificationStatus } = useAdmin();
  const [payments, setPayments] = useState([]);
  const [statistics, setStatistics] = useState({
    totalPayments: 0,
    pendingPayments: 0,
    verifiedPayments: 0,
    totalAmount: 0
  });
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({
    status: 'all',
    dateRange: 'all'
  });

  useEffect(() => {
    fetchPayments();
    fetchStatistics();
  }, [filter]);

  const fetchStatistics = async () => {
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_ADMIN_API_URL}/api/v1/admin/payments/statistics`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('admin_token')}`
          }
        }
      );
      setStatistics(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
      toast.error('Failed to load statistics');
    }
  };

  const fetchPayments = async () => {
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_ADMIN_API_URL}/api/v1/admin/payments`, 
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('admin_token')}`
          }
        }
      );
      setPayments(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching payments:', error);
      toast.error('Failed to load payments');
      setLoading(false);
    }
  };

  const handleVerification = async (paymentId, status) => {
    try {
      const note = status === 'rejected' ? prompt('Please provide a reason for rejection:') : '';
      
      await axios.post(
        `${import.meta.env.VITE_ADMIN_API_URL}/api/v1/admin/payments/${paymentId}/verify`,
        { 
          status,
          note: note || undefined
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('admin_token')}`
          }
        }
      );
      
      updateVerificationStatus('payments', paymentId, status);
      toast.success(`Payment ${status} successfully`);
      fetchPayments();
      fetchStatistics();
    } catch (error) {
      console.error('Error verifying payment:', error);
      toast.error(error.response?.data?.detail || 'Failed to verify payment');
    }
  };

  const formatAmount = (amount, currency) => {
    if (currency === 'GHS') {
      return `GH₵${amount.toLocaleString()}`;
    } else if (currency === 'NGN') {
      return `₦${amount.toLocaleString()}`;
    }
    return `${amount.toLocaleString()}`;
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4">
      <h1 className="text-2xl font-bold mb-6">Payments Management</h1>
      
      <PaymentStatistics statistics={statistics} />
      
      <div className="mb-6 flex space-x-4">
        <select
          className="border rounded-md px-3 py-2"
          value={filter.status}
          onChange={(e) => setFilter({ ...filter, status: e.target.value })}
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
        
        <select
          className="border rounded-md px-3 py-2"
          value={filter.dateRange}
          onChange={(e) => setFilter({ ...filter, dateRange: e.target.value })}
        >
          <option value="all">All Time</option>
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
        </select>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                User
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {payments.map((payment) => (
              <tr key={payment.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {payment.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {payment.user_email}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatAmount(payment.amount, payment.currency)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                    ${payment.status === 'approved' ? 'bg-green-100 text-green-800' : 
                      payment.status === 'rejected' ? 'bg-red-100 text-red-800' : 
                      'bg-yellow-100 text-yellow-800'}`}>
                    {payment.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(payment.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  {payment.status === 'pending' && (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleVerification(payment.id, 'approved')}
                        className="text-green-600 hover:text-green-900"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleVerification(payment.id, 'rejected')}
                        className="text-red-600 hover:text-red-900"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default PaymentsManagement;
