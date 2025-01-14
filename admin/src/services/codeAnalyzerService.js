import api from './api';

class CodeAnalyzerService {
  async login({ email, password }) {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.token) {
      localStorage.setItem('code_analyzer_token', response.data.token);
    }
    return response.data;
  }

  async verifyToken() {
    const response = await api.get('/verify-token');
    return response.data;
  }

  async getAnalysisRequirements() {
    const response = await api.get('/requirements');
    return response.data;
  }

  async getCountryConfig() {
    const country = localStorage.getItem('userCountry');
    if (!country) {
      throw new Error('No country selected');
    }
    const response = await api.get(`/country-config/${country}`);
    return response.data;
  }

  async getMarketplaceStats() {
    const response = await api.get('/marketplace/stats');
    return response.data;
  }

  async getSubmittedCodes(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        params.append(key, value);
      }
    });
    const response = await api.get(`/submitted-codes?${params.toString()}`);
    return response.data;
  }

  async getMarketplaceCodes(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        params.append(key, value);
      }
    });
    const response = await api.get(`/marketplace/codes?${params.toString()}`);
    return response.data;
  }

  async getTrendingCodes(timeframe = '7d') {
    const response = await api.get(`/marketplace/trending?timeframe=${timeframe}`);
    return response.data;
  }

  async searchMarketplaceCodes(params = {}) {
    // Ensure required fields are present
    const defaultParams = {
      query: '',
      sort_direction: 'desc'
    };

    // Merge with provided params and clean up null/undefined/empty values
    const mergedParams = { ...defaultParams, ...params };
    const cleanedParams = Object.entries(mergedParams).reduce((acc, [key, value]) => {
      if (value != null && value !== '') {
        acc[key] = value;
      }
      return acc;
    }, {});

    // Ensure required fields are still present after cleaning
    if (!cleanedParams.query) cleanedParams.query = '';
    if (!cleanedParams.sort_direction) cleanedParams.sort_direction = 'desc';

    const response = await api.get('/marketplace/search', { params: cleanedParams });
    return response.data;
  }

  async createAnalysis(codeId, analysisData) {
    // Log the incoming data
    console.log('Creating analysis with data:', analysisData);

    // Ensure all required fields are present and properly formatted
    if (!analysisData.analysis || !analysisData.riskLevel || !analysisData.confidenceScore) {
      throw new Error('Missing required fields: analysis, riskLevel, and confidenceScore are required');
    }

    // Format data as query parameters
    const params = new URLSearchParams({
      risk_level: analysisData.riskLevel,
      expert_analysis: analysisData.analysis,
      confidence_score: parseInt(analysisData.confidenceScore),
      recommended_price: parseFloat(analysisData.price) || 0,
      notes: analysisData.notes || ''
    });

    // Log the formatted data being sent to the API
    console.log('Sending formatted data to API:', Object.fromEntries(params));

    try {
      const response = await api.post(`/analyze/${codeId}?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('API Error Response:', error.response?.data);
      if (error.response?.data?.detail) {
        throw new Error(typeof error.response.data.detail === 'object' 
          ? JSON.stringify(error.response.data.detail) 
          : error.response.data.detail);
      }
      throw error;
    }
  }

  async publishToMarketplace(codeId, marketplaceData) {
    const response = await api.post(`/codes/${codeId}/publish`, marketplaceData);
    return response.data;
  }

  async updateMarketplaceListing(codeId, updateData) {
    const response = await api.patch(`/marketplace/codes/${codeId}`, updateData);
    return response.data;
  }

  async removeFromMarketplace(codeId) {
    const response = await api.delete(`/marketplace/codes/${codeId}`);
    return response.data;
  }

  async getCodeAnalytics(codeId) {
    const response = await api.get(`/codes/${codeId}/analytics`);
    return response.data;
  }

  async getMarketplaceAnalytics(timeframe = '7d') {
    const response = await api.get(`/marketplace/analytics?timeframe=${timeframe}`);
    return response.data;
  }

  async validateCode(codeData) {
    const response = await api.post('/validate', codeData);
    return response.data;
  }

  async getBookmakers() {
    const response = await api.get('/bookmakers');
    return response.data;
  }

  async getMarketplaceCategories() {
    const response = await api.get('/marketplace/categories');
    return response.data;
  }

  async rateCode(codeId, rating, comment = null) {
    const response = await api.post(`/codes/${codeId}/rate`, {
      rating,
      comment
    });
    return response.data;
  }

  async getCodeRatings(codeId, skip = 0, limit = 10) {
    const response = await api.get(`/codes/${codeId}/ratings?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async searchCodes(query, filters = {}) {
    const params = new URLSearchParams({ query, ...filters });
    const response = await api.get(`/search?${params.toString()}`);
    return response.data;
  }

  async getRecommendations(params = {}) {
    const queryParams = new URLSearchParams(params);
    const response = await api.get(`/marketplace/recommendations?${queryParams.toString()}`);
    return response.data;
  }

  async getMarketplacePerformance(timeframe = '30d') {
    const response = await api.get(`/marketplace/performance?timeframe=${timeframe}`);
    return response.data;
  }

  async getSimilarCodes(codeId, limit = 5) {
    const response = await api.get(`/codes/${codeId}/similar?limit=${limit}`);
    return response.data;
  }

  async getPerformanceByCategory(timeframe = '30d') {
    const response = await api.get(`/marketplace/performance?timeframe=${timeframe}`);
    return response.data.success_rates.by_category;
  }

  async getOptimalPricing(timeframe = '30d') {
    const response = await api.get(`/marketplace/performance?timeframe=${timeframe}`);
    return response.data.price_performance;
  }

  async getPopularCategories(timeframe = '30d') {
    const response = await api.get(`/marketplace/performance?timeframe=${timeframe}`);
    return response.data.popular_categories;
  }

  async getAiAnalysis(codeId) {
    const response = await api.post(`/analyze/${codeId}/ai`);
    return response.data;
  }

  async uploadToMarketplace(uploadData) {
    const response = await api.post('/marketplace/admin/upload', uploadData);
    return response.data;
  }

  async getAvailableCountries() {
    const response = await api.get('/countries');
    return response.data;
  }
}

export const codeAnalyzerService = new CodeAnalyzerService(); 