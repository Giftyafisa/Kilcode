import { toast } from 'react-hot-toast';

class WebSocketManager {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.listeners = new Map();
    }

    connect(country, token) {
        const WS_URL = import.meta.env.VITE_WS_URL;
        
        try {
            this.socket = new WebSocket(`${WS_URL}/ws/admin/${country}?token=${token}`);

            this.socket.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
            };

            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };

            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                toast.error('Connection error occurred');
            };

            this.socket.onclose = () => {
                console.log('WebSocket closed');
                this.handleReconnect(country, token);
            };

        } catch (error) {
            console.error('WebSocket connection error:', error);
            toast.error('Failed to establish connection');
        }
    }

    handleMessage(data) {
        const listeners = this.listeners.get(data.type) || [];
        listeners.forEach(callback => callback(data));

        // Show notifications for specific events
        switch (data.type) {
            case 'NEW_BETTING_CODE':
                toast.info(`New betting code from ${data.data.user_name}`);
                break;
            case 'CODE_VERIFIED':
                toast.success(`Code ${data.data.code_id} verified as ${data.data.status}`);
                break;
            case 'CHAT_MESSAGE':
                // Only notify if the message is from the user
                if (data.data.sender !== 'admin') {
                    toast.info(`New message from user: ${data.data.user_name}`);
                }
                break;
            case 'SYSTEM_ERROR':
                toast.error(data.data.message);
                break;
        }
    }

    handleReconnect(country, token) {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connect(country, token);
            }, 5000 * this.reconnectAttempts);
        } else {
            toast.error('Connection lost. Please refresh the page.');
        }
    }

    addListener(type, callback) {
        if (!this.listeners.has(type)) {
            this.listeners.set(type, []);
        }
        this.listeners.get(type).push(callback);
    }

    removeListener(type, callback) {
        if (this.listeners.has(type)) {
            const callbacks = this.listeners.get(type);
            this.listeners.set(type, callbacks.filter(cb => cb !== callback));
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
}

export const wsManager = new WebSocketManager(); 