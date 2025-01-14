import axios from 'axios';

class PaymentService {
    constructor() {
        this.api = axios.create({
            baseURL: '/api/v1/admin'
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

    async getPendingWithdrawals() {
        try {
            const response = await this.api.get('/payments/withdrawals/pending');
            return response.data;
        } catch (error) {
            console.error('Error fetching pending withdrawals:', error);
            throw this.handleError(error, 'Failed to fetch pending withdrawals');
        }
    }

    async getPaymentStatistics() {
        try {
            const response = await this.api.get('/payments/statistics');
            return response.data;
        } catch (error) {
            console.error('Error fetching payment statistics:', error);
            throw this.handleError(error, 'Failed to fetch payment statistics');
        }
    }

    async verifyPayment(paymentId, status, note = '') {
        try {
            const response = await this.api.post(`/payments/${paymentId}/verify`, {
                status,
                note
            });
            return response.data;
        } catch (error) {
            console.error('Error verifying payment:', error);
            throw this.handleError(error, 'Failed to verify payment');
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

export const paymentService = new PaymentService(); 