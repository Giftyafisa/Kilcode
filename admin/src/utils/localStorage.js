const STORAGE_PREFIX = 'admin_chat_';

export const localStorageUtil = {
    // Chat related storage
    setChatHistory: (codeId, messages) => {
        try {
            localStorage.setItem(
                `${STORAGE_PREFIX}chat_${codeId}`, 
                JSON.stringify(messages)
            );
        } catch (error) {
            console.error('Failed to save chat history:', error);
        }
    },

    getChatHistory: (codeId) => {
        try {
            const history = localStorage.getItem(`${STORAGE_PREFIX}chat_${codeId}`);
            return history ? JSON.parse(history) : [];
        } catch (error) {
            console.error('Failed to get chat history:', error);
            return [];
        }
    },

    // Unread messages counter
    setUnreadCount: (codeId, count) => {
        try {
            localStorage.setItem(
                `${STORAGE_PREFIX}unread_${codeId}`, 
                count.toString()
            );
        } catch (error) {
            console.error('Failed to save unread count:', error);
        }
    },

    getUnreadCount: (codeId) => {
        try {
            return parseInt(localStorage.getItem(`${STORAGE_PREFIX}unread_${codeId}`)) || 0;
        } catch (error) {
            console.error('Failed to get unread count:', error);
            return 0;
        }
    },

    // Clear old data
    clearOldChats: () => {
        try {
            const now = new Date().getTime();
            const THIRTY_DAYS = 30 * 24 * 60 * 60 * 1000;

            Object.keys(localStorage)
                .filter(key => key.startsWith(STORAGE_PREFIX))
                .forEach(key => {
                    const data = localStorage.getItem(key);
                    if (data) {
                        const parsed = JSON.parse(data);
                        if (parsed.timestamp && (now - parsed.timestamp > THIRTY_DAYS)) {
                            localStorage.removeItem(key);
                        }
                    }
                });
        } catch (error) {
            console.error('Failed to clear old chats:', error);
        }
    }
}; 