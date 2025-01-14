import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useAdmin } from '../context/AdminContext';
import CodeVerification from '../components/CodeVerification';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import { FaSearch, FaFilter, FaSort, FaDownload, FaSync } from 'react-icons/fa';
import { wsManager } from '../utils/websocketManager';
import { exportToCSV } from '../utils/bettingUtils';
import { bettingService } from '../services/bettingService';

// Helper function to get error message
const getErrorMessage = (error) => {
  if (typeof error === 'string') return error;
  if (error.response?.data?.detail) return error.response.data.detail;
  if (error.message) return error.message;
  return 'An unexpected error occurred';
};

function BettingCodesDashboard() {
  const { user } = useAuth();
  const [pendingCodes, setPendingCodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState({
    status: 'pending',
    bookmaker: 'all',
    dateRange: 'all',
    country: user?.country?.toLowerCase() || 'all'
  });
  const [sortConfig, setSortConfig] = useState({
    key: 'created_at',
    direction: 'desc'
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [dashboardStats, setDashboardStats] = useState({
    total: 0,
    pending: 0,
    won: 0,
    lost: 0
  });
  const [groupedView, setGroupedView] = useState(true);
  const [expandedUsers, setExpandedUsers] = useState(new Set());

  const ADMIN_API_URL = import.meta.env.VITE_ADMIN_API_URL;
  const WS_URL = import.meta.env.VITE_WS_URL;

  const [wsError, setWsError] = useState(null);
  const [reconnectCount, setReconnectCount] = useState(0);
  const MAX_RECONNECT_ATTEMPTS = 5;

  useEffect(() => {
    let reconnectTimer;
    const connectWebSocket = () => {
      try {
        const adminToken = localStorage.getItem('admin_token');
        const ws = new WebSocket(`${WS_URL}/ws/admin/${user.country.toLowerCase()}?token=${adminToken}`);
        
        ws.onopen = () => {
          console.log('WebSocket connected successfully');
          setWsError(null);
          setReconnectCount(0);
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
              case 'NEW_BETTING_CODE':
                setPendingCodes(prev => {
                  const exists = prev.some(code => code.id === data.code.id);
                  if (exists) return prev;
                  return [data.code, ...prev];
                });
                toast.info(`New betting code from ${data.code.user_name}`, {
                  duration: 5000,
                  icon: '🎲'
                });
                break;

              case 'CODE_VERIFIED':
                toast.success(`Code ${data.code_id} verified as ${data.status}`, {
                  duration: 5000,
                  icon: '✅'
                });
                fetchPendingCodes(); // Refresh list
                break;

              case 'ERROR':
                toast.error(data.message || 'Unknown error occurred', {
                  duration: 7000,
                  icon: '⚠️'
                });
                break;

              default:
                console.log('Unknown message type:', data.type);
            }
          } catch (error) {
            console.error('Error processing WebSocket message:', error);
            toast.error('Error processing update', {
              icon: '❌'
            });
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setWsError('Connection error occurred');
          toast.error('Connection error occurred', {
            icon: '🔌'
          });
        };

        ws.onclose = () => {
          console.log('WebSocket closed');
          
          if (reconnectCount < MAX_RECONNECT_ATTEMPTS) {
            toast.error(`Connection lost. Attempting to reconnect (${reconnectCount + 1}/${MAX_RECONNECT_ATTEMPTS})`, {
              duration: 3000,
              icon: '🔄'
            });
            
            if (reconnectTimer) clearTimeout(reconnectTimer);
            
            reconnectTimer = setTimeout(() => {
              setReconnectCount(prev => prev + 1);
              if (ws.readyState === WebSocket.CLOSED) {
                connectWebSocket();
              }
            }, 5000);
          } else {
            setWsError('Maximum reconnection attempts reached. Please refresh the page.');
            toast.error('Connection lost. Please refresh the page.', {
              duration: 0, // Won't auto-dismiss
              icon: '⚠️'
            });
          }
        };

        return ws;
      } catch (error) {
        console.error('WebSocket connection error:', error);
        setWsError('Failed to establish connection');
        toast.error('Failed to establish connection', {
          icon: '❌'
        });
        return null;
      }
    };

    const ws = connectWebSocket();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [user.country, reconnectCount]);

  useEffect(() => {
    fetchPendingCodes();
  }, []);

  const fetchPendingCodes = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Fetching pending codes...');
      const codes = await bettingService.getPendingCodes(filter.status !== 'all' ? filter.status : null);
      console.log('Received codes:', codes);
      
      setPendingCodes(Array.isArray(codes) ? codes : []);
      
      // Update dashboard stats
      const newStats = (Array.isArray(codes) ? codes : []).reduce((acc, code) => {
        acc.total++;
        acc[code.status]++;
        return acc;
      }, { total: 0, pending: 0, won: 0, lost: 0 });
      
      setDashboardStats(newStats);
      
    } catch (error) {
      console.error('Error fetching codes:', error);
      const errorMessage = getErrorMessage(error);
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleVerification = async (codeId, status, note = '') => {
    try {
      setLoading(true);
      
      // Validate status
      if (!['won', 'lost', 'pending'].includes(status)) {
        throw new Error('Invalid status. Must be won, lost, or pending');
      }

      await bettingService.verifyCode(codeId, {
        status,
        note: note || null
      });
      
      // Update local state to remove verified code
      setPendingCodes(prevCodes => 
        prevCodes.map(code => 
          code.id === codeId 
            ? { ...code, status: status, admin_note: note, verified_at: new Date().toISOString() }
            : code
        )
      );
      
      toast.success(`Code ${codeId} marked as ${status}`, {
        duration: 3000,
        icon: getStatusIcon(status)
      });
      
      // Refresh the list to update stats
      await fetchPendingCodes();
    } catch (error) {
      console.error('Verification error:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleInfoRequest = async (codeId, requestDetails) => {
    try {
      await bettingService.requestAdditionalInfo(codeId, requestDetails);
      toast.success('Additional information requested from user');
      fetchPendingCodes();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'won': return '✅';
      case 'lost': return '❌';
      case 'pending': return '⏳';
      case 'needs_info': return '❓';
      case 'processing': return '🔄';
      default: return '📋';
    }
  };

  const handleFilterChange = (filterType, value) => {
    setFilter(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const getFilteredAndSortedCodes = () => {
    let filtered = [...pendingCodes];

    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(code => 
        code.user_name?.toLowerCase().includes(searchLower) ||
        code.code?.toLowerCase().includes(searchLower) ||
        code.bookmaker?.toLowerCase().includes(searchLower)
      );
    }

    if (filter.status !== 'all') {
      filtered = filtered.filter(code => code.status === filter.status);
    }
    if (filter.bookmaker !== 'all') {
      filtered = filtered.filter(code => code.bookmaker === filter.bookmaker);
    }
    if (filter.dateRange !== 'all') {
      const now = new Date();
      const past = new Date();
      
      switch (filter.dateRange) {
        case 'today':
          past.setHours(0, 0, 0, 0);
          break;
        case 'week':
          past.setDate(now.getDate() - 7);
          break;
        case 'month':
          past.setMonth(now.getMonth() - 1);
          break;
        default:
          break;
      }
      
      filtered = filtered.filter(code => {
        const codeDate = new Date(code.created_at);
        return codeDate >= past && codeDate <= now;
      });
    }

    if (sortConfig.key) {
      filtered.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) 
          return sortConfig.direction === 'asc' ? -1 : 1;
        if (a[sortConfig.key] > b[sortConfig.key]) 
          return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return filtered;
  };

  const exportToCSV = () => {
    const filteredData = getFilteredAndSortedCodes();
    const headers = ['User', 'Bookmaker', 'Code', 'Odds', 'Stake', 'Potential Win', 'Date', 'Status'];
    const csvData = filteredData.map(code => [
      code.user_name,
      code.bookmaker,
      code.code,
      code.odds,
      code.stake,
      code.potential_winnings,
      new Date(code.created_at).toLocaleDateString(),
      code.status
    ]);

    const csvContent = [headers, ...csvData]
      .map(row => row.join(','))
      .join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `betting-codes-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const handleRefresh = () => {
    fetchPendingCodes();
    toast.success('Refreshing betting codes...', {
      duration: 2000,
      icon: '🔄'
    });
  };

  const groupCodesByUser = (codes) => {
    return codes.reduce((groups, code) => {
      const userId = code.user_id;
      if (!groups[userId]) {
        groups[userId] = {
          user_name: code.user_name,
          user_id: userId,
          codes: []
        };
      }
      groups[userId].codes.push(code);
      return groups;
    }, {});
  };

  const handleBulkVerification = async (userId, status, note = '') => {
    try {
      setLoading(true);
      const userCodes = groupedCodes[userId].codes;
      
      for (const code of userCodes) {
        await handleVerification(code.id, status, {
          note: note || `Bulk verification: ${status}`
        });
      }
      
      toast.success(`All codes for ${groupedCodes[userId].user_name} marked as ${status}`);
      fetchPendingCodes();
    } catch (error) {
      toast.error(`Failed to verify codes: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleUserExpanded = (userId) => {
    setExpandedUsers(prev => {
      const newSet = new Set(prev);
      if (newSet.has(userId)) {
        newSet.delete(userId);
      } else {
        newSet.add(userId);
      }
      return newSet;
    });
  };

  const renderUserCard = (group) => {
    const isExpanded = expandedUsers.has(group.user_id);
    
    return (
      <div key={group.user_id} className="mb-4 bg-white rounded-lg shadow-md overflow-hidden">
        <div 
          className="p-4 bg-gray-50 flex justify-between items-center cursor-pointer hover:bg-gray-100"
          onClick={() => toggleUserExpanded(group.user_id)}
        >
          <div>
            <h3 className="text-lg font-semibold">{group.user_name}</h3>
            <p className="text-sm text-gray-600">
              {group.codes.length} pending code{group.codes.length !== 1 ? 's' : ''}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex space-x-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleBulkVerification(group.user_id, 'won');
                }}
                className="px-3 py-1 text-sm rounded-md bg-green-100 hover:bg-green-200"
              >
                Verify All Won
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleBulkVerification(group.user_id, 'lost');
                }}
                className="px-3 py-1 text-sm rounded-md bg-red-100 hover:bg-red-200"
              >
                Verify All Lost
              </button>
            </div>
            <div className="transform transition-transform duration-200" style={{
              transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)'
            }}>
              ▼
            </div>
          </div>
        </div>
        
        {isExpanded && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Bookmaker
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Code
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Odds
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Stake
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Potential Win
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {group.codes.map((code) => (
                  <tr key={code.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {code.bookmaker}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap font-mono">
                      {code.code}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {code.odds}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {code.stake}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {code.potential_winnings}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {new Date(code.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <CodeVerification 
                        code={code}
                        onVerify={async (codeId, status, note) => {
                          await handleVerification(codeId, status, note);
                        }}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  };

  const renderGroupedView = () => {
    const groupedCodes = groupCodesByUser(getFilteredAndSortedCodes());
    return Object.values(groupedCodes).map(group => renderUserCard(group));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (wsError) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-red-500 mb-4">{wsError}</div>
        <button
          onClick={() => window.location.reload()}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Refresh Page
        </button>
      </div>
    );
  }

  const filteredCodes = getFilteredAndSortedCodes();
  
  if (pendingCodes.length === 0) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Betting Codes Dashboard</h1>
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <p className="text-gray-500 mb-4">No betting codes available</p>
          <button
            onClick={handleRefresh}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            <FaSync className="inline mr-2" />
            Refresh
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Betting Codes Dashboard</h1>
        <div className="flex space-x-4">
          <button
            onClick={handleRefresh}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 flex items-center"
            disabled={loading}
          >
            <FaSync className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={() => exportToCSV(filteredCodes)}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 flex items-center"
          >
            <FaDownload className="mr-2" />
            Export CSV
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-gray-500">Total Codes</h3>
          <p className="text-2xl font-bold">{dashboardStats.total}</p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg shadow">
          <h3 className="text-gray-500">Pending</h3>
          <p className="text-2xl font-bold text-yellow-600">{dashboardStats.pending}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg shadow">
          <h3 className="text-gray-500">Won</h3>
          <p className="text-2xl font-bold text-green-600">{dashboardStats.won}</p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg shadow">
          <h3 className="text-gray-500">Lost</h3>
          <p className="text-2xl font-bold text-red-600">{dashboardStats.lost}</p>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <FaSearch className="absolute left-3 top-3 text-gray-400" />
          </div>

          <select
            className="w-full py-2 rounded-lg border focus:ring-2 focus:ring-blue-500"
            value={filter.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
          >
            <option value="pending">Pending Verification</option>
            <option value="all">All Codes</option>
            <option value="won">Won Codes</option>
            <option value="lost">Lost Codes</option>
          </select>

          <select
            className="rounded-md border-gray-300"
            value={filter.bookmaker}
            onChange={(e) => handleFilterChange('bookmaker', e.target.value)}
          >
            <option value="all">All Bookmakers</option>
            <option value="bet9ja">Bet9ja</option>
            <option value="sportybet">SportyBet</option>
            <option value="1xbet">1xBet</option>
          </select>

          <select
            className="rounded-md border-gray-300"
            value={filter.dateRange}
            onChange={(e) => handleFilterChange('dateRange', e.target.value)}
          >
            <option value="all">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>

          <div className="flex items-center">
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                className="form-checkbox h-5 w-5 text-blue-600"
                checked={groupedView}
                onChange={(e) => setGroupedView(e.target.checked)}
              />
              <span className="ml-2 text-gray-700">Group by User</span>
            </label>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {renderGroupedView()}
      </div>
    </div>
  );
}

export default BettingCodesDashboard; 