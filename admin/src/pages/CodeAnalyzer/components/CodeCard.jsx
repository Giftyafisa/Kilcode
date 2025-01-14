import React, { useState } from 'react';
import { 
  FaChartLine, FaMoneyBillWave, FaGlobe, FaUserAlt, FaCalendarAlt, 
  FaCheckCircle, FaShoppingCart, FaExclamationTriangle, FaStar, 
  FaRegStar, FaThumbsUp, FaEye, FaChartBar
} from 'react-icons/fa';
import MarketplacePanel from './MarketplacePanel';
import { toast } from 'react-hot-toast';

const CodeCard = ({ 
  code, 
  countryConfig, 
  onAnalyze, 
  onPublish, 
  onRate,
  isSubmitted,
  isMarketplace,
  isRecommended 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat(countryConfig?.locale || 'en-US', {
      style: 'currency',
      currency: countryConfig?.currency?.code || 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString(countryConfig?.locale || 'en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handlePublish = async (marketplaceData) => {
    try {
      setIsPublishing(true);
      await onPublish(code.id, {
        ...marketplaceData,
        isPublished: true
      });
      toast.success('Code published to marketplace successfully');
    } catch (error) {
      toast.error('Failed to publish code to marketplace');
      console.error('Publish error:', error);
    } finally {
      setIsPublishing(false);
    }
  };

  const handleRateSubmit = async () => {
    try {
      await onRate(code.id, rating, comment);
      setShowRatingModal(false);
      setRating(0);
      setComment('');
    } catch (error) {
      toast.error('Failed to submit rating');
    }
  };

  const getStatusColor = () => {
    if (code.analysis_status === 'in_progress') return 'text-blue-500';
    if (code.analysis_status === 'pending') return 'text-yellow-500';
    if (code.analysis_status === 'completed') return 'text-green-500';
    if (code.marketplace_status === 'active') return 'text-green-500';
    if (code.marketplace_status === 'expired') return 'text-red-500';
    if (code.isAnalyzed) return 'text-green-500';
    return 'text-gray-500';
  };

  const getStatusText = () => {
    if (code.analysis_status === 'in_progress') return 'Analysis in Progress';
    if (code.analysis_status === 'pending') return 'Pending Analysis';
    if (code.analysis_status === 'completed') return 'Analysis Complete';
    if (code.marketplace_status === 'active') return 'Active in Marketplace';
    if (code.marketplace_status === 'expired') return 'Expired';
    if (code.marketplace_status === 'draft') return 'Draft';
    if (code.isAnalyzed) return 'Analysis Complete';
    return 'Pending';
  };

  const shouldShowAnalyzeButton = () => {
    return isSubmitted && 
           code.analysis_status !== 'in_progress' && 
           code.analysis_status !== 'completed' &&
           (!code.isAnalyzed || code.analysis_status === 'pending');
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg overflow-hidden ${isRecommended ? 'border-2 border-yellow-400' : ''}`}>
      {/* Header Section */}
      <div className="p-4 border-b">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold flex items-center space-x-2">
              <span>{code.title || 'Betting Code'}</span>
              {code.marketplace_status === 'active' && (
                <FaShoppingCart className="text-green-500" title="Active in Marketplace" />
              )}
              {code.risk_level === 'high' && (
                <FaExclamationTriangle className="text-red-500" title="High Risk" />
              )}
              {isRecommended && (
                <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
                  Recommended
                </span>
              )}
            </h3>
            <div className="flex items-center space-x-2 text-sm text-gray-600 mt-1">
              <FaGlobe className="text-blue-500" />
              <span>{countryConfig?.name}</span>
              <span>•</span>
              <FaUserAlt className="text-green-500" />
              <span>{code.issuer}</span>
              <span>•</span>
              <FaCalendarAlt className="text-purple-500" />
              <span>{formatDate(code.created_at)}</span>
            </div>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-blue-500 hover:text-blue-700"
          >
            {isExpanded ? 'Show Less' : 'Show More'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="flex items-center space-x-2">
            <FaChartLine className="text-blue-500" />
            <div>
              <p className="text-sm text-gray-600">Win Probability</p>
              <p className="font-semibold">{code.win_probability || 0}%</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <FaMoneyBillWave className="text-green-500" />
            <div>
              <p className="text-sm text-gray-600">Price</p>
              <p className="font-semibold">{formatCurrency(code.price || 0)}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <FaCheckCircle className={getStatusColor()} />
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className="font-semibold">{getStatusText()}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="text-sm">
              <p className="text-gray-600">Expected Odds</p>
              <p className="font-semibold">{code.expected_odds || 'N/A'}</p>
            </div>
          </div>
        </div>

        {/* Analysis Status */}
        {code.analysis_status === 'in_progress' && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center text-blue-600">
              <FaChartBar className="mr-2 animate-spin" />
              <span>Analysis in Progress...</span>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Please wait while we analyze your code. This may take a few moments.
            </p>
          </div>
        )}

        {/* Analyze Button */}
        {shouldShowAnalyzeButton() && (
          <div className="mt-4">
            <button
              onClick={() => onAnalyze(code.id)}
              className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center justify-center"
              disabled={code.analysis_status === 'in_progress'}
            >
              <FaChartBar className="mr-2" />
              {code.analysis_status === 'in_progress' ? 'Analysis in Progress' : 'Analyze Code'}
            </button>
          </div>
        )}

        {/* Stats Bar */}
        {isMarketplace && (
          <div className="mt-4 flex items-center space-x-6 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <FaEye className="text-gray-400" />
              <span>{code.stats?.views || 0} views</span>
            </div>
            <div className="flex items-center space-x-1">
              <FaThumbsUp className="text-gray-400" />
              <span>{code.stats?.purchases || 0} purchases</span>
            </div>
            <div className="flex items-center space-x-1">
              <FaStar className="text-yellow-400" />
              <span>{code.stats?.rating?.toFixed(1) || 0} rating</span>
            </div>
          </div>
        )}

        {/* Expanded Content */}
        {isExpanded && (
          <div className="mt-4 border-t pt-4">
            {/* Code Details */}
            <div className="mb-4">
              <h4 className="font-semibold mb-2">Code Details</h4>
              <p className="text-gray-600">{code.description || 'No description available'}</p>
            </div>

            {/* Analysis Section */}
            {!isSubmitted && code.expert_analysis && (
              <div className="mb-4">
                <h4 className="font-semibold mb-2">Expert Analysis</h4>
                <p className="text-gray-600">{code.expert_analysis}</p>
              </div>
            )}

            {/* Rating Section */}
            {isMarketplace && (
              <div className="mb-4">
                <h4 className="font-semibold mb-2">Rate this Code</h4>
                <div className="flex items-center space-x-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => setRating(star)}
                      className="focus:outline-none"
                    >
                      {star <= rating ? (
                        <FaStar className="text-yellow-400 text-xl" />
                      ) : (
                        <FaRegStar className="text-gray-400 text-xl" />
                      )}
                    </button>
                  ))}
                </div>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Write your review (optional)"
                  className="mt-2 w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  rows="3"
                />
                <button
                  onClick={handleRateSubmit}
                  disabled={!rating}
                  className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  Submit Rating
                </button>
              </div>
            )}

            {/* Marketplace Panel */}
            {!isSubmitted && (
              <MarketplacePanel
                code={code}
                countryConfig={countryConfig}
                onPublish={handlePublish}
                isPublishing={isPublishing}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeCard; 