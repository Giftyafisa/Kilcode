import React from 'react';
import { FaTimes, FaCheck, FaBan } from 'react-icons/fa';

function VerificationDetailsModal({ isOpen, onClose, data, onVerify }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Verification Details</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <FaTimes />
          </button>
        </div>

        <div className="space-y-4">
          {/* User Information */}
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="font-semibold mb-2">User Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Name</p>
                <p className="font-medium">{data.user.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium">{data.user.email}</p>
              </div>
            </div>
          </div>

          {/* Transaction Details */}
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="font-semibold mb-2">Transaction Details</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Amount</p>
                <p className="font-medium">{data.amount} {data.currency}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Method</p>
                <p className="font-medium">{data.method}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Date</p>
                <p className="font-medium">
                  {new Date(data.created_at).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="font-medium">{data.status}</p>
              </div>
            </div>
          </div>

          {/* Verification Actions */}
          <div className="flex justify-end space-x-4 mt-6">
            <button
              onClick={() => onVerify(data.id, 'rejected')}
              className="flex items-center px-4 py-2 bg-red-100 text-red-800 rounded hover:bg-red-200"
            >
              <FaBan className="mr-2" />
              Reject
            </button>
            <button
              onClick={() => onVerify(data.id, 'approved')}
              className="flex items-center px-4 py-2 bg-green-100 text-green-800 rounded hover:bg-green-200"
            >
              <FaCheck className="mr-2" />
              Approve
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VerificationDetailsModal; 