import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  FaChartBar,
  FaExclamationTriangle,
  FaCheckCircle,
  FaHistory,
  FaComments
} from 'react-icons/fa';
import { toast } from 'react-hot-toast';

const DetailedAnalysis = ({ code, aiAnalysis, onSubmitAnalysis }) => {
  const [activeTab, setActiveTab] = useState('ai');
  const [isExpanded, setIsExpanded] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [expertAnalysis, setExpertAnalysis] = useState({
    analysis: '',
    confidenceScore: 50,
    riskLevel: 'medium',
    price: '0',
    notes: ''
  });
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');

  const handleSubmit = useCallback(async () => {
    if (isSubmitting) return;

    if (!expertAnalysis.analysis.trim()) {
      toast.error('Please provide your expert analysis');
      return;
    }
    if (!expertAnalysis.riskLevel) {
      toast.error('Please select a risk level');
      return;
    }
    if (!expertAnalysis.confidenceScore) {
      toast.error('Please set a confidence score');
      return;
    }

    try {
      setIsSubmitting(true);
      const formattedAnalysis = {
        analysis: expertAnalysis.analysis.trim(),
        riskLevel: expertAnalysis.riskLevel,
        confidenceScore: parseInt(expertAnalysis.confidenceScore),
        price: expertAnalysis.price ? parseFloat(expertAnalysis.price) : 0,
        notes: expertAnalysis.notes ? expertAnalysis.notes.trim() : ''
      };

      console.log('Submitting analysis:', formattedAnalysis);
      await onSubmitAnalysis(formattedAnalysis);
    } finally {
      setIsSubmitting(false);
    }
  }, [expertAnalysis, onSubmitAnalysis, isSubmitting]);

  const addComment = () => {
    if (!newComment.trim()) return;
    setComments([
      ...comments,
      {
        id: Date.now(),
        text: newComment,
        timestamp: new Date().toISOString()
      }
    ]);
    setNewComment('');
  };

  const tabs = [
    { id: 'ai', label: 'AI Analysis', icon: FaChartBar },
    { id: 'expert', label: 'Expert Analysis', icon: FaCheckCircle },
    { id: 'risk', label: 'Risk Assessment', icon: FaExclamationTriangle },
    { id: 'history', label: 'Analysis History', icon: FaHistory },
    { id: 'comments', label: 'Comments', icon: FaComments }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-lg p-6"
    >
      {/* Tabs */}
      <div className="flex space-x-4 mb-6 border-b">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center px-4 py-2 space-x-2 border-b-2 transition-colors ${
              activeTab === id
                ? 'border-blue-500 text-blue-500'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Icon className="w-4 h-4" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'ai' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            {!aiAnalysis ? (
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <p className="text-gray-600">Loading AI analysis...</p>
              </div>
            ) : (
              <>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-lg mb-2">AI Analysis Summary</h3>
                  <p className="text-gray-700">{aiAnalysis.summary || 'No summary available'}</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-lg mb-2">Code Details</h3>
                  <div className="space-y-2">
                    <div>
                      <span className="font-medium text-gray-700">Description: </span>
                      <span className="text-gray-600">{code?.description || 'No description available'}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Bookmaker: </span>
                      <span className="text-gray-600">{code?.bookmaker || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Odds: </span>
                      <span className="text-gray-600">{code?.odds || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Stake: </span>
                      <span className="text-gray-600">{code?.stake || 'N/A'}</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-700">Confidence Score</h4>
                    <div className="mt-2 flex items-center">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${aiAnalysis.confidenceScore || 0}%` }}
                          className="bg-blue-500 h-2 rounded-full"
                        />
                      </div>
                      <span className="ml-2 text-sm font-medium">
                        {aiAnalysis.confidenceScore || 0}%
                      </span>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-700">Risk Level</h4>
                    <div className="mt-2">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          (aiAnalysis.risk || 'high') === 'low'
                            ? 'bg-green-100 text-green-800'
                            : (aiAnalysis.risk || 'high') === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {(aiAnalysis.risk || 'HIGH').toUpperCase()}
                      </span>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-700">Pattern Match</h4>
                    <div className="mt-2">
                      {aiAnalysis.details?.patternAnalysis?.matchesFormat ? (
                        <span className="text-green-500">✓ Valid Format</span>
                      ) : (
                        <span className="text-red-500">✗ Invalid Format</span>
                      )}
                    </div>
                  </div>
                </div>

                {aiAnalysis.recommendations?.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-700 mb-2">Recommendations</h4>
                    <ul className="list-disc list-inside space-y-1">
                      {aiAnalysis.recommendations.map((rec, index) => (
                        <li key={index} className="text-gray-600">{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </motion.div>
        )}

        {activeTab === 'expert' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Expert Analysis
              </label>
              <textarea
                value={expertAnalysis.analysis}
                onChange={(e) =>
                  setExpertAnalysis({ ...expertAnalysis, analysis: e.target.value })
                }
                rows={4}
                className="w-full p-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your detailed analysis..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confidence Score
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={expertAnalysis.confidenceScore}
                  onChange={(e) =>
                    setExpertAnalysis({
                      ...expertAnalysis,
                      confidenceScore: parseInt(e.target.value)
                    })
                  }
                  className="w-full"
                />
                <div className="text-center text-sm text-gray-500">
                  {expertAnalysis.confidenceScore}%
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Risk Level
                </label>
                <select
                  value={expertAnalysis.riskLevel}
                  onChange={(e) =>
                    setExpertAnalysis({ ...expertAnalysis, riskLevel: e.target.value })
                  }
                  className="w-full p-2 border rounded-lg"
                >
                  <option value="low">Low Risk</option>
                  <option value="medium">Medium Risk</option>
                  <option value="high">High Risk</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Price
                </label>
                <input
                  type="number"
                  value={expertAnalysis.price}
                  onChange={(e) =>
                    setExpertAnalysis({ ...expertAnalysis, price: e.target.value })
                  }
                  className="w-full p-2 border rounded-lg"
                  placeholder="Enter price..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Additional Notes
                </label>
                <input
                  type="text"
                  value={expertAnalysis.notes}
                  onChange={(e) =>
                    setExpertAnalysis({ ...expertAnalysis, notes: e.target.value })
                  }
                  className="w-full p-2 border rounded-lg"
                  placeholder="Any additional notes..."
                />
              </div>
            </div>

            <div className="flex justify-end">
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className={`px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Analysis'}
              </button>
            </div>
          </motion.div>
        )}

        {activeTab === 'risk' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            {!aiAnalysis ? (
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <p className="text-gray-600">Loading risk assessment...</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-700">Odds Analysis</h4>
                  <div className="mt-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-600">Score:</span>
                      <span className="text-sm font-medium">
                        {((aiAnalysis.details?.oddsAnalysis?.score || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Within Limits:</span>
                      <span
                        className={`text-sm font-medium ${
                          aiAnalysis.details?.oddsAnalysis?.isWithinLimits
                            ? 'text-green-500'
                            : 'text-red-500'
                        }`}
                      >
                        {aiAnalysis.details?.oddsAnalysis?.isWithinLimits ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-700">Stake Analysis</h4>
                  <div className="mt-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-600">Score:</span>
                      <span className="text-sm font-medium">
                        {((aiAnalysis.details?.stakeAnalysis?.score || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Within Limits:</span>
                      <span
                        className={`text-sm font-medium ${
                          aiAnalysis.details?.stakeAnalysis?.isWithinLimits
                            ? 'text-green-500'
                            : 'text-red-500'
                        }`}
                      >
                        {aiAnalysis.details?.stakeAnalysis?.isWithinLimits ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'comments' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <div className="flex space-x-2">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                className="flex-1 p-2 border rounded-lg"
                placeholder="Add a comment..."
              />
              <button
                onClick={addComment}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                Add
              </button>
            </div>

            <div className="space-y-2">
              {comments.map((comment) => (
                <div
                  key={comment.id}
                  className="bg-gray-50 p-3 rounded-lg"
                >
                  <p className="text-gray-700">{comment.text}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(comment.timestamp).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default DetailedAnalysis; 