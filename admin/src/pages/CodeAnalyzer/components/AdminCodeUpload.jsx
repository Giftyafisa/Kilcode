import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { FaUpload, FaGlobe, FaMoneyBillWave, FaBookmark } from 'react-icons/fa';
import { useCodeAnalyzerAuth } from '../../../context/CodeAnalyzerAuthContext';
import { codeAnalyzerService } from '../../../services/codeAnalyzerService';

const AdminCodeUpload = () => {
  const { user } = useCodeAnalyzerAuth();
  const [code, setCode] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedBookmaker, setSelectedBookmaker] = useState('');
  const [countries, setCountries] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [countryConfig, setCountryConfig] = useState(null);
  const [categories, setCategories] = useState([]);
  const [winProbability, setWinProbability] = useState('');
  const [expectedOdds, setExpectedOdds] = useState('');
  const [validityHours, setValidityHours] = useState('24');
  const [minStake, setMinStake] = useState('');
  const [category, setCategory] = useState('');

  useEffect(() => {
    const fetchCountries = async () => {
      try {
        const data = await codeAnalyzerService.getAvailableCountries();
        console.log('Countries data:', data);
        setCountries(data);
      } catch (error) {
        console.error('Error fetching countries:', error);
        toast.error('Failed to load countries');
      }
    };
    fetchCountries();
  }, []);

  useEffect(() => {
    if (selectedCountry) {
      const config = countries.find(c => c.code === selectedCountry);
      console.log('Selected country config:', config);
      setCountryConfig(config);
      setSelectedBookmaker(''); // Reset bookmaker when country changes

      // Set categories from the country config
      if (config?.marketplace_settings?.categories) {
        console.log('Setting categories:', config.marketplace_settings.categories);
        setCategories(config.marketplace_settings.categories);
      } else {
        console.log('No categories found in config');
        setCategories([]);
      }
    }
  }, [selectedCountry, countries]);

  useEffect(() => {
    if (selectedCountry) {
      const config = countries.find(c => c.code === selectedCountry);
      setCountryConfig(config);
      setSelectedBookmaker(''); // Reset bookmaker when country changes
    }
  }, [selectedCountry, countries]);

  const validateForm = () => {
    if (!countryConfig) {
      toast.error('Please select a country');
      return false;
    }

    if (!selectedBookmaker) {
      toast.error('Please select a bookmaker');
      return false;
    }

    if (!code || !title || !description || !price || !winProbability || !expectedOdds || !minStake || !category) {
      toast.error('Please fill in all required fields');
      return false;
    }

    const priceNum = parseFloat(price);
    const minPrice = countryConfig?.marketplace_settings?.min_price || 0;
    const maxPrice = countryConfig?.marketplace_settings?.max_price || Infinity;
    
    if (isNaN(priceNum) || priceNum < minPrice || priceNum > maxPrice) {
      toast.error(`Price must be between ${countryConfig.currency.symbol}${minPrice} and ${countryConfig.currency.symbol}${maxPrice}`);
      return false;
    }

    const winProbNum = parseFloat(winProbability);
    if (isNaN(winProbNum) || winProbNum < 0 || winProbNum > 100) {
      toast.error('Win probability must be between 0 and 100');
      return false;
    }

    const oddsNum = parseFloat(expectedOdds);
    const minOdds = countryConfig?.marketplace_settings?.min_odds || 1.2;
    const maxOdds = countryConfig?.marketplace_settings?.max_odds || 1000;
    
    if (isNaN(oddsNum) || oddsNum < minOdds || oddsNum > maxOdds) {
      toast.error(`Expected odds must be between ${minOdds} and ${maxOdds}`);
      return false;
    }

    const minStakeNum = parseFloat(minStake);
    const minStakeLimit = countryConfig?.marketplace_settings?.min_stake_limit || 0;
    const maxStakeLimit = countryConfig?.marketplace_settings?.max_stake_limit || Infinity;
    
    if (isNaN(minStakeNum) || minStakeNum < minStakeLimit || minStakeNum > maxStakeLimit) {
      toast.error(`Minimum stake must be between ${countryConfig.currency.symbol}${minStakeLimit} and ${countryConfig.currency.symbol}${maxStakeLimit}`);
      return false;
    }

    const validityHoursNum = parseInt(validityHours);
    const maxValidityHours = countryConfig?.marketplace_settings?.max_validity_hours || 72;
    if (isNaN(validityHoursNum) || validityHoursNum < 1 || validityHoursNum > maxValidityHours) {
      toast.error(`Validity period must be between 1 and ${maxValidityHours} hours`);
      return false;
    }

    if (description.length < (countryConfig?.marketplace_settings?.min_description_length || 50)) {
      toast.error(`Description must be at least ${countryConfig?.marketplace_settings?.min_description_length || 50} characters long`);
      return false;
    }

    if (title.length < (countryConfig?.marketplace_settings?.min_title_length || 10)) {
      toast.error(`Title must be at least ${countryConfig?.marketplace_settings?.min_title_length || 10} characters long`);
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      // Format the data according to country-specific requirements
      const uploadData = {
        code: code.trim(),
        title: title.trim(),
        description: description.trim(),
        price: parseFloat(price),
        bookmaker: selectedBookmaker,
        winProbability: parseFloat(winProbability),
        expectedOdds: parseFloat(expectedOdds),
        validityPeriod: parseInt(validityHours),
        minStake: parseFloat(minStake),
        category,
        isPublished: true,
        marketplace_status: 'active',
        status: 'pending',  // Set initial status as pending
        odds: parseFloat(expectedOdds),
        stake: parseFloat(minStake),
        potential_winnings: parseFloat(expectedOdds) * parseFloat(minStake),
        user_country: selectedCountry.toLowerCase(),
        is_published: true,
        analysis_status: 'completed',
        valid_until: new Date(Date.now() + parseInt(validityHours) * 60 * 60 * 1000).toISOString()
      };

      console.log('Uploading code with data:', uploadData);
      
      const response = await codeAnalyzerService.uploadToMarketplace(uploadData);
      
      if (response.success) {
        toast.success('Code successfully uploaded to marketplace');
        // Reset form
        setCode('');
        setTitle('');
        setDescription('');
        setPrice('');
        setSelectedCountry('');
        setSelectedBookmaker('');
        setWinProbability('');
        setExpectedOdds('');
        setValidityHours('24');
        setMinStake('');
        setCategory('');
      } else {
        throw new Error(response.message || 'Failed to upload code');
      }
    } catch (error) {
      console.error('Error uploading code:', error);
      toast.error(error.response?.data?.detail || error.message || 'Failed to upload code');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-6">
        <FaUpload className="text-blue-500 text-xl mr-2" />
        <h2 className="text-xl font-semibold">Upload Code to Marketplace</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Country
          </label>
          <div className="flex items-center">
            <FaGlobe className="text-gray-400 mr-2" />
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="w-full p-2 border rounded-lg"
              required
            >
              <option value="">Select Country</option>
              {countries.map((country) => (
                <option key={country.code} value={country.code}>
                  {country.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {countryConfig && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bookmaker
            </label>
            <select
              value={selectedBookmaker}
              onChange={(e) => setSelectedBookmaker(e.target.value)}
              className="w-full p-2 border rounded-lg"
              required
            >
              <option value="">Select Bookmaker</option>
              {countryConfig.bookmakers.map((bm) => (
                <option key={bm.id} value={bm.id}>
                  {bm.name}
                </option>
              ))}
            </select>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-2 border rounded-lg"
            placeholder="Enter code title"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-2 border rounded-lg"
            rows="3"
            placeholder="Enter code description"
            required
          />
          {countryConfig?.marketplace_settings?.min_description_length && (
            <p className="mt-1 text-sm text-gray-500">
              Minimum {countryConfig.marketplace_settings.min_description_length} characters
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Code
          </label>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="w-full p-2 border rounded-lg font-mono"
            rows="10"
            placeholder="Paste your code here"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <div className="flex items-center">
                <FaMoneyBillWave className="text-gray-400 mr-2" />
                Price {countryConfig && `(${countryConfig.currency.symbol})`}
              </div>
            </label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="w-full p-2 border rounded-lg"
              placeholder={`Enter price${countryConfig ? ` in ${countryConfig.currency.name}` : ''}`}
              step="0.01"
              min={countryConfig?.marketplace_settings?.min_price || "0"}
              max={countryConfig?.marketplace_settings?.max_price}
              required
            />
            {countryConfig && (
              <p className="mt-1 text-sm text-gray-500">
                Min: {countryConfig.currency.symbol}{countryConfig.marketplace_settings?.min_price || 0}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Minimum Stake
            </label>
            <input
              type="number"
              value={minStake}
              onChange={(e) => setMinStake(e.target.value)}
              className="w-full p-2 border rounded-lg"
              placeholder="Enter minimum stake"
              step="0.01"
              min={countryConfig?.marketplace_settings?.min_stake_limit || "0"}
              required
            />
            {countryConfig && (
              <p className="mt-1 text-sm text-gray-500">
                Min: {countryConfig.currency.symbol}{countryConfig.marketplace_settings?.min_stake_limit || 0}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Win Probability (%)
            </label>
            <input
              type="number"
              value={winProbability}
              onChange={(e) => setWinProbability(e.target.value)}
              className="w-full p-2 border rounded-lg"
              placeholder="Enter win probability"
              min="0"
              max="100"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Expected Odds
            </label>
            <input
              type="number"
              value={expectedOdds}
              onChange={(e) => setExpectedOdds(e.target.value)}
              className="w-full p-2 border rounded-lg"
              placeholder="Enter expected odds"
              step="0.01"
              min={countryConfig?.marketplace_settings?.min_odds || "1.2"}
              max={countryConfig?.marketplace_settings?.max_odds || "1000"}
              required
            />
            {countryConfig && (
              <p className="mt-1 text-sm text-gray-500">
                Range: {countryConfig.marketplace_settings?.min_odds || 1.2} - {countryConfig.marketplace_settings?.max_odds || 1000}
              </p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Validity Period (hours)
            </label>
            <input
              type="number"
              value={validityHours}
              onChange={(e) => setValidityHours(e.target.value)}
              className="w-full p-2 border rounded-lg"
              placeholder="Enter validity period in hours"
              min="1"
              max={countryConfig?.marketplace_settings?.max_validity_hours || "72"}
              required
            />
            {countryConfig && (
              <p className="mt-1 text-sm text-gray-500">
                Max: {countryConfig.marketplace_settings?.max_validity_hours || 72} hours
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <div className="flex items-center">
                <FaBookmark className="text-gray-400 mr-2" />
                Category
              </div>
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full p-2 border rounded-lg"
              required
            >
              <option value="">Select Category</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className={`w-full py-2 px-4 rounded-lg text-white ${
            isLoading
              ? 'bg-blue-400 cursor-not-allowed'
              : 'bg-blue-500 hover:bg-blue-600'
          }`}
        >
          {isLoading ? 'Uploading...' : 'Upload to Marketplace'}
        </button>
      </form>
    </div>
  );
};

export default AdminCodeUpload;