import React, { useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import DetailedAnalysis from './DetailedAnalysis';

const AnalysisModal = ({ isOpen, onClose, code, aiAnalysis, onSubmitAnalysis }) => {
  const handleBackdropClick = useCallback((e) => {
    // Only close if clicking directly on the backdrop
    if (e.target === e.currentTarget) {
      onClose();
    }
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
        onClick={handleBackdropClick}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        >
          <div className="flex justify-between items-center p-4 border-b">
            <h2 className="text-xl font-semibold">Code Analysis</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="p-4">
            <DetailedAnalysis
              code={code}
              aiAnalysis={aiAnalysis}
              onSubmitAnalysis={onSubmitAnalysis}
            />
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AnalysisModal; 