import React, { useState } from 'react';
import { toast } from 'react-hot-toast';

function PaymentVerification({ payment, onVerify }) {
  const [loading, setLoading] = useState(false);
  const [showNoteInput, setShowNoteInput] = useState(false);
  const [note, setNote] = useState('');

  const handleVerification = async (status) => {
    if (!showNoteInput) {
      setShowNoteInput(true);
      return;
    }

    setLoading(true);
    try {
      await onVerify(payment.id, status, note);
      setShowNoteInput(false);
      setNote('');
    } catch (error) {
      toast.error('Failed to verify payment');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setShowNoteInput(false);
    setNote('');
  };

  if (payment.status !== 'pending') {
    return (
      <span className={`px-2 py-1 text-sm rounded-full ${
        payment.status === 'approved' 
          ? 'bg-green-100 text-green-800'
          : 'bg-red-100 text-red-800'
      }`}>
        {payment.status}
      </span>
    );
  }

  if (showNoteInput) {
    return (
      <div className="flex flex-col space-y-2">
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Add a note (optional)"
          className="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows="2"
        />
        <div className="flex justify-end space-x-2">
          <button
            onClick={handleCancel}
            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={() => handleVerification('approved')}
            className="px-3 py-1 text-sm bg-green-100 hover:bg-green-200 rounded-md"
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Approve'}
          </button>
          <button
            onClick={() => handleVerification('rejected')}
            className="px-3 py-1 text-sm bg-red-100 hover:bg-red-200 rounded-md"
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Reject'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex space-x-2">
      <button
        onClick={() => handleVerification('approved')}
        className="px-3 py-1 text-sm bg-green-100 hover:bg-green-200 rounded-md"
        disabled={loading}
      >
        Approve
      </button>
      <button
        onClick={() => handleVerification('rejected')}
        className="px-3 py-1 text-sm bg-red-100 hover:bg-red-200 rounded-md"
        disabled={loading}
      >
        Reject
      </button>
    </div>
  );
}

export default PaymentVerification; 