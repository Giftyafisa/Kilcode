import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { paymentService } from '../services/paymentService';
import PaymentVerification from '../components/PaymentVerification';
import PaymentStatistics from '../components/PaymentStatistics';
import { toast } from 'react-hot-toast';
import { FaSync } from 'react-icons/fa';

function PaymentAdminDashboard() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [payments, setPayments] = useState([]);
  const [statistics, setStatistics] = useState({
    totalPayments: 0,
    pendingPayments: 0,
    verifiedPayments: 0,
    totalAmount: 0
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [paymentsData, statsData] = await Promise.all([
        paymentService.getPendingWithdrawals(),
        paymentService.getPaymentStatistics()
      ]);
      
      setPayments(paymentsData);
      setStatistics(statsData);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerification = async (paymentId, status) => {
    try {
      await paymentService.verifyPayment(paymentId, status);
      toast.success(`Payment ${status} successfully`);
      fetchData(); // Refresh data
    } catch (error) {
      toast.error(error.message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Payment Admin Dashboard</h1>
        <button
          onClick={fetchData}
          className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          <FaSync className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <PaymentStatistics statistics={statistics} />

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Pending Withdrawals</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Payment Method
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {payments.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                    No pending withdrawals
                  </td>
                </tr>
              ) : (
                payments.map((payment) => (
                  <tr key={payment.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {payment.user_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {payment.user_email}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {user.country === 'nigeria' ? '₦' : 'GH₵'}
                        {payment.amount.toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {payment.payment_method}
                      </div>
                      {payment.phone && (
                        <div className="text-sm text-gray-500">
                          {payment.phone}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(payment.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                        {payment.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <PaymentVerification
                        payment={payment}
                        onVerify={handleVerification}
                      />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default PaymentAdminDashboard; 