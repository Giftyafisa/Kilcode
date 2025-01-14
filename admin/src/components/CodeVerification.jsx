import React, { useState } from 'react';
import { FaCheck, FaTimes, FaClock } from 'react-icons/fa';

function CodeVerification({ code, onVerify }) {
  const [isVerifying, setIsVerifying] = useState(false);
  const [note, setNote] = useState('');
  const [showNoteInput, setShowNoteInput] = useState(false);

  const StatusBadge = ({ status, note }) => {
    switch (status) {
      case 'won':
        return (
          <div className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-md">
            <FaCheck className="mr-1" /> Won
            {note && <span className="ml-2 text-xs">Note: {note}</span>}
          </div>
        );
      case 'lost':
        return (
          <div className="inline-flex items-center px-3 py-1 bg-red-100 text-red-800 rounded-md">
            <FaTimes className="mr-1" /> Lost
            {note && <span className="ml-2 text-xs">Note: {note}</span>}
          </div>
        );
      default:
        return (
          <div className="inline-flex items-center px-3 py-1 bg-yellow-100 text-yellow-800 rounded-md">
            <FaClock className="mr-1" /> Pending
          </div>
        );
    }
  };

  const handleVerification = async (status) => {
    if (!['won', 'lost', 'pending'].includes(status)) {
      console.error('Invalid status:', status);
      return;
    }

    if (showNoteInput) {
      setIsVerifying(true);
      try {
        await onVerify(code.id, status, note);
        setShowNoteInput(false);
        setNote('');
      } catch (error) {
        console.error('Verification error:', error);
      } finally {
        setIsVerifying(false);
      }
    } else {
      setShowNoteInput(true);
    }
  };

  const handleCancel = () => {
    setShowNoteInput(false);
    setNote('');
  };

  // If code is already verified, only show status badge
  if (code.status === 'won' || code.status === 'lost') {
    return <StatusBadge status={code.status} note={code.admin_note} />;
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
            disabled={isVerifying}
          >
            Cancel
          </button>
          <button
            onClick={() => handleVerification('won')}
            className="px-3 py-1 text-sm bg-green-100 hover:bg-green-200 rounded-md flex items-center"
            disabled={isVerifying}
          >
            <FaCheck className="mr-1" /> {isVerifying ? 'Verifying...' : 'Mark Won'}
          </button>
          <button
            onClick={() => handleVerification('lost')}
            className="px-3 py-1 text-sm bg-red-100 hover:bg-red-200 rounded-md flex items-center"
            disabled={isVerifying}
          >
            <FaTimes className="mr-1" /> {isVerifying ? 'Verifying...' : 'Mark Lost'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2">
      <StatusBadge status={code.status} />
      <button
        onClick={() => handleVerification('won')}
        className="px-3 py-1 text-sm bg-green-100 hover:bg-green-200 rounded-md flex items-center"
        disabled={isVerifying}
      >
        <FaCheck className="mr-1" /> Won
      </button>
      <button
        onClick={() => handleVerification('lost')}
        className="px-3 py-1 text-sm bg-red-100 hover:bg-red-200 rounded-md flex items-center"
        disabled={isVerifying}
      >
        <FaTimes className="mr-1" /> Lost
      </button>
    </div>
  );
}

export default CodeVerification; 