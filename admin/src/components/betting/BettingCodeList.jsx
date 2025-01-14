import React, { useState } from 'react';
import { FaSearch, FaFilter, FaSort } from 'react-icons/fa';
import CodeVerification from '../CodeVerification';

function BettingCodeList({ 
    codes, 
    onVerify, 
    onSort, 
    onFilter, 
    onSearch,
    sortConfig,
    loading 
}) {
    const [searchTerm, setSearchTerm] = useState('');
    const [filters, setFilters] = useState({
        status: 'all',
        bookmaker: 'all',
        dateRange: 'all'
    });

    const handleSearch = (e) => {
        const value = e.target.value;
        setSearchTerm(value);
        onSearch(value);
    };

    const handleFilterChange = (type, value) => {
        const newFilters = { ...filters, [type]: value };
        setFilters(newFilters);
        onFilter(newFilters);
    };

    const handleSort = (key) => {
        onSort(key);
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Filters and Search */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-white p-4 rounded-lg shadow">
                <div className="relative">
                    <input
                        type="text"
                        placeholder="Search codes..."
                        className="w-full pl-10 pr-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500"
                        value={searchTerm}
                        onChange={handleSearch}
                    />
                    <FaSearch className="absolute left-3 top-3 text-gray-400" />
                </div>

                <select
                    className="w-full py-2 rounded-lg border focus:ring-2 focus:ring-blue-500"
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                >
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="won">Won</option>
                    <option value="lost">Lost</option>
                </select>

                <select
                    className="w-full py-2 rounded-lg border focus:ring-2 focus:ring-blue-500"
                    value={filters.bookmaker}
                    onChange={(e) => handleFilterChange('bookmaker', e.target.value)}
                >
                    <option value="all">All Bookmakers</option>
                    <option value="bet9ja">Bet9ja</option>
                    <option value="sportybet">SportyBet</option>
                    <option value="1xbet">1xBet</option>
                </select>

                <select
                    className="w-full py-2 rounded-lg border focus:ring-2 focus:ring-blue-500"
                    value={filters.dateRange}
                    onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                >
                    <option value="all">All Time</option>
                    <option value="today">Today</option>
                    <option value="week">This Week</option>
                    <option value="month">This Month</option>
                </select>
            </div>

            {/* Codes Table */}
            <div className="bg-white rounded-lg shadow overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            {[
                                { key: 'user_name', label: 'User' },
                                { key: 'bookmaker', label: 'Bookmaker' },
                                { key: 'code', label: 'Code' },
                                { key: 'odds', label: 'Odds' },
                                { key: 'stake', label: 'Stake' },
                                { key: 'potential_winnings', label: 'Potential Win' },
                                { key: 'created_at', label: 'Date' },
                                { key: 'actions', label: 'Actions' }
                            ].map(({ key, label }) => (
                                <th
                                    key={key}
                                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                    onClick={() => key !== 'actions' && handleSort(key)}
                                >
                                    <div className="flex items-center space-x-1">
                                        <span>{label}</span>
                                        {sortConfig?.key === key && (
                                            <FaSort className="text-gray-400" />
                                        )}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {codes.map((code) => (
                            <tr key={code.id}>
                                <td className="px-6 py-4 whitespace-nowrap">{code.user_name}</td>
                                <td className="px-6 py-4 whitespace-nowrap">{code.bookmaker}</td>
                                <td className="px-6 py-4 whitespace-nowrap">{code.code}</td>
                                <td className="px-6 py-4 whitespace-nowrap">{code.odds}</td>
                                <td className="px-6 py-4 whitespace-nowrap">{code.stake}</td>
                                <td className="px-6 py-4 whitespace-nowrap">{code.potential_winnings}</td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {new Date(code.created_at).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <CodeVerification
                                        code={code}
                                        onVerify={(status) => onVerify(code.id, status)}
                                    />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default BettingCodeList; 