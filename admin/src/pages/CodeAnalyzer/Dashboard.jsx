import React, { useState, useEffect } from 'react';
import { codeAnalyzerService } from '../../services/codeAnalyzerService';
import { useCodeAnalyzerAuth } from '../../context/CodeAnalyzerAuthContext';
import StatCard from './components/StatCard';
import CodeCard from './components/CodeCard';
import StatisticalAnalysis from './components/StatisticalAnalysis';
import CodeSortingPanel from './components/CodeSortingPanel';
import { 
  FaCode, FaChartLine, FaMoneyBillWave, FaShoppingCart, 
  FaChartBar, FaRegStar, FaRegLightbulb, FaRegClock
} from 'react-icons/fa';
import { toast } from 'react-hot-toast';
import AnalysisModal from './components/AnalysisModal';

const Dashboard = () => {
  const { user, country } = useCodeAnalyzerAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [submittedCodes, setSubmittedCodes] = useState([]);
  const [marketplaceCodes, setMarketplaceCodes] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [countryConfig, setCountryConfig] = useState(null);
  const [activeTab, setActiveTab] = useState('submitted');
  const [timeframe, setTimeframe] = useState('30d');
  const [filters, setFilters] = useState({
    bookmaker: null,
    minOdds: null,
    maxOdds: null,
    startDate: null,
    endDate: null,
    sortBy: null,
    sortDirection: 'desc',
    status: null,
    priceRange: null,
    category: null,
    minRating: null
  });
  const [selectedCode, setSelectedCode] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const sortOptions = [
    { value: 'win_probability', label: 'Win Probability' },
    { value: 'odds', label: 'Odds' },
    { value: 'price', label: 'Price' },
    { value: 'created_at', label: 'Date' },
    { value: 'rating', label: 'Rating' },
    { value: 'popularity', label: 'Popularity' }
  ];

  const statusOptions = [
    { value: 'pending', label: 'Pending Analysis' },
    { value: 'analyzed', label: 'Analyzed' },
    { value: 'published', label: 'Published' },
    { value: 'expired', label: 'Expired' }
  ];

  const timeframeOptions = [
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' }
  ];

  useEffect(() => {
    if (country) {
      localStorage.setItem('userCountry', country);
      loadDashboardData();
    }
  }, [country, filters, activeTab, timeframe]);

  const loadDashboardData = async () => {
    if (!country) {
      console.error('No country selected');
      return;
    }

    try {
      setLoading(true);
      
      // Load country configuration
      const config = await codeAnalyzerService.getCountryConfig();
      setCountryConfig(config);
      
      // Load marketplace stats and performance
      const [marketplaceStats, performanceData] = await Promise.all([
        codeAnalyzerService.getMarketplaceStats(),
        codeAnalyzerService.getMarketplacePerformance(timeframe)
      ]);
      
      setStats(marketplaceStats);
      setPerformance(performanceData);

      // Load recommendations with cleaned parameters
      const recommendationParams = {
        ...(filters.category && { category: filters.category }),
        min_success_rate: 0.7,
        ...(filters.priceRange?.max && { max_price: filters.priceRange.max })
      };
      const recommendedCodes = await codeAnalyzerService.getRecommendations(recommendationParams);
      setRecommendations(recommendedCodes);

      // Load appropriate codes based on active tab
      if (activeTab === 'submitted') {
        // Clean up filters by removing null/undefined values
        const cleanedFilters = Object.entries(filters).reduce((acc, [key, value]) => {
          if (value != null && value !== '') {
            acc[key] = value;
          }
          return acc;
        }, {});
        
        const codes = await codeAnalyzerService.getSubmittedCodes(cleanedFilters);
        
        // Preserve the selected code's state if it exists
        if (selectedCode) {
          setSubmittedCodes(Array.isArray(codes) ? codes.map(code => 
            code.id === selectedCode.id ? { ...code, ...selectedCode } : code
          ) : []);
        } else {
          setSubmittedCodes(Array.isArray(codes) ? codes : []);
        }
      } else {
        // Clean up search parameters
        const searchParams = {
          query: filters.search || '',
          sort_direction: filters.sortDirection || 'desc',
          ...(filters.minRating && { min_rating: filters.minRating }),
          ...(filters.minWinRate && { min_win_rate: filters.minWinRate }),
          ...(filters.category && { category: filters.category }),
          ...(filters.bookmaker && { bookmaker: filters.bookmaker }),
          ...(filters.priceRange?.min && { min_price: filters.priceRange.min }),
          ...(filters.priceRange?.max && { max_price: filters.priceRange.max }),
          ...(filters.sortBy && { sort_by: filters.sortBy })
        };
        
        const codes = await codeAnalyzerService.searchMarketplaceCodes(searchParams);
        setMarketplaceCodes(Array.isArray(codes) ? codes : []);
      }

    } catch (error) {
      console.error('Error loading dashboard data:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Error loading dashboard data';
      toast.error(String(errorMessage));
    } finally {
      setLoading(false);
    }
  };

  const handleSortChange = (sortValue) => {
    setFilters({
      ...filters,
      sortBy: sortValue,
      sortDirection: sortValue === filters.sortBy && filters.sortDirection === 'desc' ? 'asc' : 'desc'
    });
  };

  const handleTimeframeChange = (value) => {
    setTimeframe(value);
  };

  const handleAnalyze = async (codeId) => {
    try {
      setIsAnalyzing(true);
      const code = submittedCodes.find(c => c.id === codeId);
      setSelectedCode(code);
      
      // Get AI analysis
      const analysis = await codeAnalyzerService.getAiAnalysis(codeId);
      setAiAnalysis(analysis);
    } catch (error) {
      console.error('Error analyzing code:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Error getting AI analysis';
      toast.error(String(errorMessage));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmitAnalysis = async (analysisData) => {
    try {
      const response = await codeAnalyzerService.createAnalysis(selectedCode.id, analysisData);
      
      // Update the code in submittedCodes with the new analysis status
      const updatedCode = {
        ...selectedCode,
        ...response,
        analysis_status: 'in_progress',
        expert_analysis: analysisData.analysis,
        risk_level: analysisData.riskLevel,
        confidence_score: analysisData.confidenceScore,
        price: analysisData.price,
        notes: analysisData.notes,
        isAnalyzed: true
      };

      // Update the selected code first
      setSelectedCode(updatedCode);

      // Update the code in submittedCodes while preserving the array
      setSubmittedCodes(prevCodes => {
        const updatedCodes = prevCodes.map(code => 
          code.id === selectedCode.id ? updatedCode : code
        );
        return updatedCodes;
      });

      // Clear only the AI analysis state
      setAiAnalysis(null);
      toast.success('Analysis submitted successfully');

      // Keep checking the analysis status until it's complete
      const checkAnalysisStatus = async () => {
        try {
          const codes = await codeAnalyzerService.getSubmittedCodes(filters);
          const updatedCodeStatus = codes.find(c => c.id === selectedCode.id);
          
          if (updatedCodeStatus) {
            // Preserve the existing code data while updating the status
            const mergedCode = {
              ...updatedCode,
              ...updatedCodeStatus,
              isAnalyzed: true // Ensure this flag stays true
            };
            
            setSubmittedCodes(prevCodes => 
              prevCodes.map(code => 
                code.id === selectedCode.id ? mergedCode : code
              )
            );
            
            if (updatedCodeStatus.analysis_status !== 'in_progress') {
              // Analysis is complete, but don't close the modal yet
              toast.success('Analysis completed successfully');
              // Update one final time with completed status
              setSubmittedCodes(prevCodes => 
                prevCodes.map(code => 
                  code.id === selectedCode.id ? { ...mergedCode, analysis_status: 'completed' } : code
                )
              );
              // Now we can close the modal
              setSelectedCode(null);
            } else {
              // Check again in 5 seconds
              setTimeout(checkAnalysisStatus, 5000);
            }
          }
        } catch (error) {
          console.error('Error checking analysis status:', error);
          // Don't close the modal or remove the code on error
        }
      };

      // Start checking the analysis status
      checkAnalysisStatus();
    } catch (error) {
      console.error('Error submitting analysis:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Error submitting analysis';
      toast.error(String(errorMessage));
      // Don't close the modal or remove the code on error
    }
  };

  const handlePublish = async (codeId, marketplaceData) => {
    try {
      await codeAnalyzerService.publishToMarketplace(codeId, marketplaceData);
      loadDashboardData();
      toast.success('Code published to marketplace');
    } catch (error) {
      console.error('Error publishing code:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Error publishing code';
      toast.error(String(errorMessage));
    }
  };

  const handleRateCode = async (codeId, rating, comment) => {
    try {
      await codeAnalyzerService.rateCode(codeId, rating, comment);
      loadDashboardData();
      toast.success('Rating submitted successfully');
    } catch (error) {
      console.error('Error rating code:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Error submitting rating';
      toast.error(String(errorMessage));
    }
  };

  if (!country) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-red-600">Please select a country to continue</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Active Listings"
          value={stats?.active_listings || 0}
          icon={<FaShoppingCart />}
          color="blue"
        />
        <StatCard
          title="Success Rate"
          value={`${performance?.success_rates?.overall.toFixed(1) || 0}%`}
          icon={<FaChartLine />}
          color="green"
        />
        <StatCard
          title="Total Revenue"
          value={stats?.total_revenue?.toLocaleString() || 0}
          icon={<FaMoneyBillWave />}
          color="purple"
        />
        <StatCard
          title="Optimal Price Range"
          value={performance?.price_performance?.optimal_range || 'N/A'}
          icon={<FaChartBar />}
          color="yellow"
        />
      </div>

      {/* Performance Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Performance Overview</h2>
          <select
            value={timeframe}
            onChange={(e) => handleTimeframeChange(e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            {timeframeOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Category Performance */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Top Categories</h3>
            <div className="space-y-2">
              {performance?.popular_categories?.map(cat => (
                <div key={cat.category} className="flex justify-between items-center">
                  <span className="text-sm">{cat.category}</span>
                  <span className="text-sm font-medium">{cat.purchases} sales</span>
                </div>
              ))}
            </div>
          </div>

          {/* Price Performance */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Price Performance</h3>
            <div className="space-y-2">
              {performance?.price_performance?.by_range?.map(range => (
                <div key={range.range} className="flex justify-between items-center">
                  <span className="text-sm">{range.range}</span>
                  <span className="text-sm font-medium">{range.success_rate.toFixed(1)}% success</span>
                </div>
              ))}
            </div>
          </div>

          {/* Success Rates */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Success Rates by Category</h3>
            <div className="space-y-2">
              {Object.entries(performance?.success_rates?.by_category || {}).map(([category, rate]) => (
                <div key={category} className="flex justify-between items-center">
                  <span className="text-sm">{category}</span>
                  <span className="text-sm font-medium">{rate.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations Section */}
      {activeTab === 'marketplace' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <FaRegLightbulb className="mr-2 text-yellow-500" />
            Recommended Codes
          </h2>
          <div className="grid grid-cols-1 gap-4">
            {recommendations.map(code => (
              <CodeCard
                key={code.id}
                code={code}
                countryConfig={countryConfig}
                onAnalyze={handleAnalyze}
                onPublish={handlePublish}
                onRate={handleRateCode}
                isRecommended={true}
              />
            ))}
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('submitted')}
            className={`${
              activeTab === 'submitted'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Submitted Codes
          </button>
          <button
            onClick={() => setActiveTab('marketplace')}
            className={`${
              activeTab === 'marketplace'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Marketplace
          </button>
        </nav>
      </div>

      {/* Advanced Sorting and Filtering Panel */}
      <CodeSortingPanel
        filters={filters}
        setFilters={setFilters}
        sortOptions={sortOptions}
        statusOptions={statusOptions}
        countryData={countryConfig}
        onSortChange={handleSortChange}
        activeTab={activeTab}
      />

      {/* Codes Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold flex items-center">
          <FaRegClock className="mr-2" />
          {activeTab === 'submitted' ? 'Submitted Codes' : 'Marketplace Codes'}
        </h2>
        <div className="grid grid-cols-1 gap-4">
          {(activeTab === 'submitted' ? submittedCodes : marketplaceCodes).length === 0 ? (
            <div className="bg-white rounded-lg p-8">
              <p className="text-gray-500 text-center">
                No {activeTab === 'submitted' ? 'submitted' : 'marketplace'} codes found for {country?.toUpperCase()}
              </p>
            </div>
          ) : (
            (activeTab === 'submitted' ? submittedCodes : marketplaceCodes).map((code) => (
              <CodeCard
                key={code.id}
                code={code}
                countryConfig={countryConfig}
                onAnalyze={handleAnalyze}
                onPublish={handlePublish}
                onRate={handleRateCode}
                isSubmitted={activeTab === 'submitted'}
                isMarketplace={activeTab === 'marketplace'}
              />
            ))
          )}
        </div>
      </div>

      {/* Analysis Modal */}
      <AnalysisModal
        isOpen={!!selectedCode}
        onClose={() => {
          setSelectedCode(null);
          setAiAnalysis(null);
        }}
        code={selectedCode}
        aiAnalysis={aiAnalysis}
        onSubmitAnalysis={handleSubmitAnalysis}
      />
    </div>
  );
};

export default Dashboard; 