import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { bettingService } from '../services/bettingService';
import { wsManager } from '../utils/websocketManager';
import { filterCodes, sortCodes } from '../utils/bettingUtils';

export const useBettingCodes = (country) => {
    const [codes, setCodes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({
        status: 'all',
        bookmaker: 'all',
        dateRange: 'all'
    });
    const [sortConfig, setSortConfig] = useState({
        key: 'created_at',
        direction: 'desc'
    });
    const [searchTerm, setSearchTerm] = useState('');

    const fetchCodes = useCallback(async () => {
        try {
            setLoading(true);
            const data = await bettingService.getPendingCodes();
            setCodes(data);
        } catch (error) {
            setError(error.message);
            toast.error(error.message);
        } finally {
            setLoading(false);
        }
    }, []);

    const handleVerification = useCallback(async (codeId, status, note) => {
        try {
            await bettingService.verifyCode(codeId, status, note);
            toast.success('Code verification updated successfully');
            fetchCodes();
        } catch (error) {
            toast.error(error.message);
        }
    }, [fetchCodes]);

    useEffect(() => {
        fetchCodes();

        // Connect to WebSocket
        const token = localStorage.getItem('admin_token');
        wsManager.connect(country, token);

        // Add WebSocket listeners
        wsManager.addListener('NEW_BETTING_CODE', (data) => {
            setCodes(prev => [data.code, ...prev]);
            toast.info(`New betting code from ${data.code.user_name}`);
        });

        return () => {
            wsManager.disconnect();
        };
    }, [country, fetchCodes]);

    const filteredAndSortedCodes = useCallback(() => {
        const filtered = filterCodes(codes, filters, searchTerm);
        return sortCodes(filtered, sortConfig);
    }, [codes, filters, searchTerm, sortConfig]);

    return {
        codes: filteredAndSortedCodes(),
        loading,
        error,
        filters,
        setFilters,
        sortConfig,
        setSortConfig,
        searchTerm,
        setSearchTerm,
        handleVerification,
        refreshCodes: fetchCodes
    };
}; 