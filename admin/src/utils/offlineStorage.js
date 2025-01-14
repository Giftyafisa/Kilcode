import { localStorageUtil } from './localStorage';

class OfflineStorage {
    constructor() {
        this.pendingMessages = new Map();
        this.syncInterval = null;
        this.SYNC_INTERVAL = 5000; // 5 seconds
    }

    addPendingMessage(codeId, message) {
        if (!this.pendingMessages.has(codeId)) {
            this.pendingMessages.set(codeId, []);
        }
        this.pendingMessages.get(codeId).push({
            ...message,
            pendingId: `pending_${Date.now()}_${Math.random()}`
        });
        this.savePendingMessages();
    }

    removePendingMessage(codeId, pendingId) {
        const messages = this.pendingMessages.get(codeId) || [];
        this.pendingMessages.set(
            codeId,
            messages.filter(msg => msg.pendingId !== pendingId)
        );
        this.savePendingMessages();
    }

    savePendingMessages() {
        try {
            const data = Object.fromEntries(this.pendingMessages);
            localStorage.setItem('pending_messages', JSON.stringify(data));
        } catch (error) {
            console.error('Failed to save pending messages:', error);
        }
    }

    loadPendingMessages() {
        try {
            const data = localStorage.getItem('pending_messages');
            if (data) {
                const parsed = JSON.parse(data);
                this.pendingMessages = new Map(Object.entries(parsed));
            }
        } catch (error) {
            console.error('Failed to load pending messages:', error);
        }
    }

    startSync(syncCallback) {
        this.stopSync();
        this.syncInterval = setInterval(() => {
            if (navigator.onLine && this.pendingMessages.size > 0) {
                this.pendingMessages.forEach((messages, codeId) => {
                    messages.forEach(message => {
                        syncCallback(codeId, message)
                            .then(() => this.removePendingMessage(codeId, message.pendingId))
                            .catch(error => console.error('Failed to sync message:', error));
                    });
                });
            }
        }, this.SYNC_INTERVAL);
    }

    stopSync() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
        }
    }
}

export const offlineStorage = new OfflineStorage(); 