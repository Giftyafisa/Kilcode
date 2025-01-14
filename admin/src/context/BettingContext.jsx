import React, { createContext, useContext, useReducer } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const BettingContext = createContext(null);

const initialState = {
  pendingCodes: [],
  verifiedCodes: [],
  statistics: {
    totalCodes: 0,
    pendingCodes: 0,
    wonCodes: 0,
    lostCodes: 0,
    totalPayout: 0
  },
  filters: {
    status: 'all',
    bookmaker: 'all',
    dateRange: 'all'
  },
  loading: false,
  error: null
};

const bettingReducer = (state, action) => {
  switch (action.type) {
    case 'SET_PENDING_CODES':
      return {
        ...state,
        pendingCodes: action.payload,
        loading: false
      };
      
    case 'SET_VERIFIED_CODES':
      return {
        ...state,
        verifiedCodes: action.payload,
        loading: false
      };
      
    case 'UPDATE_CODE_STATUS':
      const { codeId, status } = action.payload;
      const updatedPending = state.pendingCodes.filter(code => code.id !== codeId);
      const updatedCode = state.pendingCodes.find(code => code.id === codeId);
      
      if (updatedCode) {
        updatedCode.status = status;
        return {
          ...state,
          pendingCodes: updatedPending,
          verifiedCodes: [...state.verifiedCodes, updatedCode]
        };
      }
      return state;
      
    case 'SET_STATISTICS':
      return {
        ...state,
        statistics: action.payload
      };
      
    case 'SET_FILTERS':
      return {
        ...state,
        filters: {
          ...state.filters,
          ...action.payload
        }
      };
      
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload
      };
      
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false
      };
      
    default:
      return state;
  }
};

export const BettingProvider = ({ children }) => {
  const [state, dispatch] = useReducer(bettingReducer, initialState);
  const API_URL = import.meta.env.VITE_ADMIN_API_URL;

  // Fetch pending betting codes
  const fetchPendingCodes = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const token = localStorage.getItem('admin_token');
      const response = await axios.get(
        `${API_URL}/api/v1/admin/betting-codes/pending`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      dispatch({ type: 'SET_PENDING_CODES', payload: response.data });
    } catch (error) {
      console.error('Error fetching pending codes:', error);
      toast.error('Failed to fetch pending codes');
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  // Verify betting code
  const verifyCode = async (codeId, status, note = '') => {
    try {
      const token = localStorage.getItem('admin_token');
      await axios.post(
        `${API_URL}/api/v1/admin/betting-codes/${codeId}/verify`,
        { status, note },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      dispatch({
        type: 'UPDATE_CODE_STATUS',
        payload: { codeId, status }
      });
      
      toast.success(`Code marked as ${status}`);
      await fetchPendingCodes(); // Refresh the list
    } catch (error) {
      console.error('Error verifying code:', error);
      toast.error('Failed to verify code');
    }
  };

  // Update filters
  const updateFilters = (filters) => {
    dispatch({ type: 'SET_FILTERS', payload: filters });
  };

  const value = {
    state,
    fetchPendingCodes,
    verifyCode,
    updateFilters
  };

  return (
    <BettingContext.Provider value={value}>
      {children}
    </BettingContext.Provider>
  );
};

export const useBetting = () => {
  const context = useContext(BettingContext);
  if (!context) {
    throw new Error('useBetting must be used within a BettingProvider');
  }
  return context;
}; 