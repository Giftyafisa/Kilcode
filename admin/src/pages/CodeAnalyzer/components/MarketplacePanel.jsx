import React, { useState } from 'react';
import { FaShoppingCart, FaSpinner, FaTags, FaChartLine, FaMoneyBillWave } from 'react-icons/fa';
import { toast } from 'react-hot-toast';

const MarketplacePanel = ({ code, countryConfig, onPublish, isPublishing }) => {
  const [marketplaceData, setMarketplaceData] = useState({
    price: code.price || '',
    description: code.description || '',
    winProbability: code.win_probability || '',
    expectedOdds: code.expected_odds || '',
    validityPeriod: 24,
    minStake: code.min_stake || '',
    tags: code.tags || [],
    category: code.category || '',
    customFields: code.custom_fields || {}
  });

  const [newTag, setNewTag] = useState('');
  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setMarketplaceData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when field is edited
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const handleTagAdd = () => {
    if (newTag.trim()) {
      setMarketplaceData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const handleTagRemove = (tagToRemove) => {
    setMarketplaceData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const validateForm = () => {
    const newErrors = {};
    const settings = countryConfig?.config?.marketplace_settings || {};

    if (!marketplaceData.price) {
      newErrors.price = 'Price is required';
    } else if (marketplaceData.price < settings.min_price) {
      newErrors.price = `Minimum price is ${settings.min_price}`;
    } else if (marketplaceData.price > settings.max_price) {
      newErrors.price = `Maximum price is ${settings.max_price}`;
    }

    if (!marketplaceData.description) {
      newErrors.description = 'Description is required';
    } else if (marketplaceData.description.length < settings.min_description_length) {
      newErrors.description = `Description must be at least ${settings.min_description_length} characters`;
    }

    if (!marketplaceData.winProbability) {
      newErrors.winProbability = 'Win probability is required';
    } else if (marketplaceData.winProbability < 0 || marketplaceData.winProbability > 100) {
      newErrors.winProbability = 'Win probability must be between 0 and 100';
    }

    if (!marketplaceData.expectedOdds) {
      newErrors.expectedOdds = 'Expected odds are required';
    } else if (marketplaceData.expectedOdds < settings.min_odds) {
      newErrors.expectedOdds = `Minimum odds are ${settings.min_odds}`;
    }

    if (!marketplaceData.category) {
      newErrors.category = 'Category is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) {
      toast.error('Please fix the errors before publishing');
      return;
    }

    try {
      await onPublish(marketplaceData);
    } catch (error) {
      console.error('Error publishing to marketplace:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || String(error) || 'Failed to publish to marketplace';
      toast.error(String(errorMessage));
    }
  };

  if (code.marketplace_status === 'active') {
    return (
      <div className="mt-4 p-4 bg-green-50 rounded-lg">
        <div className="flex items-center space-x-2 text-green-700">
          <FaShoppingCart />
          <span>This code is active in the marketplace</span>
        </div>
        <div className="mt-2 text-sm text-green-600">
          <p>Price: {code.price}</p>
          <p>Valid until: {new Date(code.valid_until).toLocaleDateString()}</p>
          <p>Category: {code.category}</p>
          {code.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {code.tags.map(tag => (
                <span key={tag} className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="mt-4">
      <h4 className="font-semibold mb-4 flex items-center">
        <FaShoppingCart className="mr-2" />
        Publish to Marketplace
      </h4>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Price Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              <FaMoneyBillWave className="inline mr-1" />
              Price ({countryConfig?.currency?.symbol})
            </label>
            <input
              type="number"
              name="price"
              value={marketplaceData.price}
              onChange={handleInputChange}
              className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 ${
                errors.price ? 'border-red-300' : 'border-gray-300'
              }`}
              required
            />
            {errors.price && (
              <p className="mt-1 text-sm text-red-600">{errors.price}</p>
            )}
          </div>

          {/* Win Probability Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              <FaChartLine className="inline mr-1" />
              Win Probability (%)
            </label>
            <input
              type="number"
              name="winProbability"
              value={marketplaceData.winProbability}
              onChange={handleInputChange}
              className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 ${
                errors.winProbability ? 'border-red-300' : 'border-gray-300'
              }`}
              required
            />
            {errors.winProbability && (
              <p className="mt-1 text-sm text-red-600">{errors.winProbability}</p>
            )}
          </div>

          {/* Category Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Category</label>
            <select
              name="category"
              value={marketplaceData.category}
              onChange={handleInputChange}
              className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 ${
                errors.category ? 'border-red-300' : 'border-gray-300'
              }`}
              required
            >
              <option value="">Select Category</option>
              {countryConfig?.config?.marketplace_categories?.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
            {errors.category && (
              <p className="mt-1 text-sm text-red-600">{errors.category}</p>
            )}
          </div>

          {/* Expected Odds Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Expected Odds</label>
            <input
              type="number"
              name="expectedOdds"
              value={marketplaceData.expectedOdds}
              onChange={handleInputChange}
              step="0.01"
              className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 ${
                errors.expectedOdds ? 'border-red-300' : 'border-gray-300'
              }`}
              required
            />
            {errors.expectedOdds && (
              <p className="mt-1 text-sm text-red-600">{errors.expectedOdds}</p>
            )}
          </div>

          {/* Validity Period Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Validity Period (hours)
            </label>
            <input
              type="number"
              name="validityPeriod"
              value={marketplaceData.validityPeriod}
              onChange={handleInputChange}
              min="1"
              max={countryConfig?.config?.marketplace_settings?.max_validity_hours}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {/* Minimum Stake Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Minimum Stake ({countryConfig?.currency?.symbol})
            </label>
            <input
              type="number"
              name="minStake"
              value={marketplaceData.minStake}
              onChange={handleInputChange}
              min={countryConfig?.config?.marketplace_settings?.min_stake_limit}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>
        </div>

        {/* Tags Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <FaTags className="inline mr-1" />
            Tags
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {marketplaceData.tags.map(tag => (
              <span
                key={tag}
                className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full flex items-center"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleTagRemove(tag)}
                  className="ml-1 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder="Add a tag"
              className="flex-1 rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              type="button"
              onClick={handleTagAdd}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
            >
              Add
            </button>
          </div>
        </div>

        {/* Description Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            name="description"
            value={marketplaceData.description}
            onChange={handleInputChange}
            rows="3"
            className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 ${
              errors.description ? 'border-red-300' : 'border-gray-300'
            }`}
            required
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description}</p>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isPublishing || Object.keys(errors).length > 0}
            className={`
              inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white
              ${isPublishing || Object.keys(errors).length > 0 ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}
            `}
          >
            {isPublishing ? (
              <>
                <FaSpinner className="animate-spin -ml-1 mr-2 h-4 w-4" />
                Publishing...
              </>
            ) : (
              <>
                <FaShoppingCart className="-ml-1 mr-2 h-4 w-4" />
                Publish to Marketplace
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default MarketplacePanel; 