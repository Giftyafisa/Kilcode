export const appConfig = {
    chat: {
        maxHistoryDays: 30,
        messagePageSize: 50,
        typingTimeout: 3000,
        maxFileSize: 5 * 1024 * 1024, // 5MB
        allowedFileTypes: ['image/jpeg', 'image/png', 'application/pdf'],
        messageRetention: {
            regular: 30 * 24 * 60 * 60 * 1000, // 30 days
            important: 90 * 24 * 60 * 60 * 1000 // 90 days
        }
    },
    storage: {
        prefix: 'admin_chat_',
        version: '1.0.0'
    }
}; 