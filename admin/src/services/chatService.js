import axios from 'axios';

const ADMIN_API_URL = import.meta.env.VITE_ADMIN_API_URL;

class ChatService {
    constructor() {
        this.api = axios.create({
            baseURL: `${ADMIN_API_URL}/api/v1/admin/chat`
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

    async getChatHistory(userId, codeId) {
        try {
            const response = await this.api.get(`/history/${codeId}`, {
                params: { userId }
            });
            return response.data;
        } catch (error) {
            throw this.handleError(error, 'Failed to fetch chat history');
        }
    }

    async sendMessage(userId, codeId, message) {
        try {
            const response = await this.api.post(`/send`, {
                userId,
                codeId,
                message,
                timestamp: new Date().toISOString()
            });
            return response.data;
        } catch (error) {
            throw this.handleError(error, 'Failed to send message');
        }
    }

    async markAsRead(messageIds) {
        try {
            const response = await this.api.post(`/mark-read`, {
                messageIds
            });
            return response.data;
        } catch (error) {
            throw this.handleError(error, 'Failed to mark messages as read');
        }
    }

    handleError(error, defaultMessage) {
        const message = error.response?.data?.detail || defaultMessage;
        console.error('Chat API Error:', error);
        return new Error(message);
    }
}

export const chatService = new ChatService(); 