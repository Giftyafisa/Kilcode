import React from 'react';
import { FaSort, FaFilter, FaCalendarAlt } from 'react-icons/fa';

const CodeSortingPanel = ({
  filters,
  setFilters,
  sortOptions,
  statusOptions,
  countryData,
  onSortChange,
  activeTab
}) => {
  const handleFilterChange = (name, value) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      bookmaker: null,
      minOdds: null,
      maxOdds: null,
      startDate: null,
      endDate: null,
      sortBy: null,
      sortDirection: 'desc',
      status: null,
      priceRange: null
    });
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium">Filters & Sorting</h3>
        <button
          onClick={clearFilters}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Clear All
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            value={filters.status || ''}
            onChange={(e) => handleFilterChange('status', e.target.value || null)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            {statusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Bookmaker Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Bookmaker
          </label>
          <select
            value={filters.bookmaker || ''}
            onChange={(e) => handleFilterChange('bookmaker', e.target.value || null)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">All Bookmakers</option>
            {countryData?.config?.bookmakers?.map((bookmaker) => (
              <option key={bookmaker.id} value={bookmaker.id}>
                {bookmaker.name}
              </option>
            ))}
          </select>
        </div>

        {/* Sort By */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sort By
          </label>
          <select
            value={filters.sortBy || ''}
            onChange={(e) => onSortChange(e.target.value || null)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Default Sort</option>
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label} {filters.sortBy === option.value ? (filters.sortDirection === 'desc' ? '↓' : '↑') : ''}
              </option>
            ))}
          </select>
        </div>

        {/* Odds Range */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Odds Range
          </label>
          <div className="grid grid-cols-2 gap-4">
            <input
              type="number"
              placeholder="Min Odds"
              value={filters.minOdds || ''}
              onChange={(e) => handleFilterChange('minOdds', e.target.value || null)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              min="1"
              step="0.01"
            />
            <input
              type="number"
              placeholder="Max Odds"
              value={filters.maxOdds || ''}
              onChange={(e) => handleFilterChange('maxOdds', e.target.value || null)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              min="1"
              step="0.01"
            />
          </div>
        </div>

        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Date Range
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="date"
              value={filters.startDate || ''}
              onChange={(e) => handleFilterChange('startDate', e.target.value || null)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
            <span className="text-gray-500">to</span>
            <input
              type="date"
              value={filters.endDate || ''}
              onChange={(e) => handleFilterChange('endDate', e.target.value || null)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Price Range (Only for Marketplace) */}
        {activeTab === 'marketplace' && (
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Price Range ({countryData?.config?.currency?.symbol || '$'})
            </label>
            <div className="grid grid-cols-2 gap-4">
              <input
                type="number"
                placeholder="Min Price"
                value={filters.minPrice || ''}
                onChange={(e) => handleFilterChange('minPrice', e.target.value || null)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="0"
                step="0.01"
              />
              <input
                type="number"
                placeholder="Max Price"
                value={filters.maxPrice || ''}
                onChange={(e) => handleFilterChange('maxPrice', e.target.value || null)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="0"
                step="0.01"
              />
            </div>
          </div>
        )}
      </div>

      {/* Active Filters Summary */}
      <div className="mt-4 flex flex-wrap gap-2">
        {Object.entries(filters).map(([key, value]) => {
          if (!value) return null;
          return (
            <span
              key={key}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            >
              {key.replace(/([A-Z])/g, ' $1').toLowerCase()}: {value}
              <button
                onClick={() => handleFilterChange(key, null)}
                className="ml-1 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          );
        })}
      </div>
    </div>
  );
};

export default CodeSortingPanel; 