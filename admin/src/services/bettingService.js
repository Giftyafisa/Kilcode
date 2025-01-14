import axios from 'axios';
import { wsManager } from '../utils/websocketManager';

class BettingService {
    constructor() {
        this.api = axios.create({
            baseURL: '/api/v1/admin'  // Use relative URL for proxy
        });

        // Add token to all requests
        this.api.interceptors.request.use((config) => {
            const token = localStorage.getItem('admin_token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });
    }

    async getPendingCodes(status = null) {
        try {
            const url = status ? 
                `/betting-codes/pending?status=${status}` : 
                '/betting-codes/pending';
                
            console.log('Fetching betting codes from:', url);
            const response = await this.api.get(url);
            console.log('Betting codes response:', response.data);
            return response.data;
        } catch (error) {
            console.error('Error fetching betting codes:', error);
            throw this.handleError(error, 'Failed to fetch betting codes');
        }
    }

    async verifyCode(codeId, data) {
        try {
            // Validate required fields
            if (!codeId) {
                throw new Error('Code ID is required');
            }
            if (!data || !data.status) {
                throw new Error('Status is required');
            }
            if (!['won', 'lost', 'pending'].includes(data.status)) {
                throw new Error('Invalid status. Must be won, lost, or pending');
            }

            console.log('Verifying code with data:', data);
            
            const response = await this.api.post(
                `/betting-codes/${codeId}/verify?status=${data.status}`, 
                { note: data.note || null }
            );

            // After successful verification, notify through WebSocket if socket is connected
            if (wsManager && wsManager.socket && wsManager.socket.readyState === WebSocket.OPEN) {
                wsManager.socket.send(JSON.stringify({
                    type: 'CODE_VERIFIED',
                    data: {
                        code_id: codeId,
                        status: data.status,
                        note: data.note,
                        verified_at: new Date().toISOString()
                    }
                }));
            }

            return response.data;
        } catch (error) {
            console.error('Error verifying code:', error);
            throw this.handleError(error, 'Failed to verify betting code');
        }
    }

    async addVerificationNote(codeId, note) {
        try {
            const response = await this.api.post(`/betting-codes/${codeId}/notes`, { note });
            return response.data;
        } catch (error) {
            throw this.handleError(error, 'Failed to add verification note');
        }
    }

    async requestAdditionalInfo(codeId, requestDetails) {
        try {
            const response = await this.api.post(`/betting-codes/${codeId}/request-info`, {
                requestDetails
            });
            return response.data;
        } catch (error) {
            throw this.handleError(error, 'Failed to request additional information');
        }
    }

    async getStatistics() {
        try {
            const response = await this.api.get('/betting-codes/statistics');
            return response.data;
        } catch (error) {
            throw this.handleError(error, 'Failed to fetch statistics');
        }
    }

    handleError(error, defaultMessage) {
        console.error('API Error:', error.response || error);
        
        if (error.response?.data?.detail) {
            const detail = error.response.data.detail;
            if (typeof detail === 'string') {
                return new Error(detail);
            }
            if (Array.isArray(detail)) {
                return new Error(detail.map(err => err.msg || err.message).join(', '));
            }
            return new Error(JSON.stringify(detail));
        }
        
        if (error.message) {
            return new Error(error.message);
        }
        
        return new Error(defaultMessage || 'An unexpected error occurred');
    }
}

export const bettingService = new BettingService(); 