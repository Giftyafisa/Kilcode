import React, { createContext, useContext, useReducer } from 'react';
import { chatService } from '../services/chatService';

const ChatContext = createContext(null);

const initialState = {
    activeChats: {},
    unreadMessages: {},
    typingUsers: {}
};

const chatReducer = (state, action) => {
    switch (action.type) {
        case 'SET_CHAT_HISTORY':
            return {
                ...state,
                activeChats: {
                    ...state.activeChats,
                    [action.payload.codeId]: action.payload.messages
                }
            };
        
        case 'ADD_MESSAGE':
            const { codeId, message } = action.payload;
            return {
                ...state,
                activeChats: {
                    ...state.activeChats,
                    [codeId]: [
                        ...(state.activeChats[codeId] || []),
                        message
                    ]
                }
            };

        case 'SET_TYPING':
            return {
                ...state,
                typingUsers: {
                    ...state.typingUsers,
                    [action.payload.userId]: action.payload.isTyping
                }
            };

        case 'MARK_AS_READ':
            return {
                ...state,
                unreadMessages: {
                    ...state.unreadMessages,
                    [action.payload.codeId]: 0
                }
            };

        default:
            return state;
    }
};

export const ChatProvider = ({ children }) => {
    const [state, dispatch] = useReducer(chatReducer, initialState);

    const value = {
        state,
        dispatch,
        // Helper functions
        loadChatHistory: async (userId, codeId) => {
            try {
                const messages = await chatService.getChatHistory(userId, codeId);
                dispatch({
                    type: 'SET_CHAT_HISTORY',
                    payload: { codeId, messages }
                });
            } catch (error) {
                console.error('Failed to load chat history:', error);
            }
        },
        sendMessage: async (userId, codeId, message) => {
            try {
                const response = await chatService.sendMessage(userId, codeId, message);
                dispatch({
                    type: 'ADD_MESSAGE',
                    payload: { codeId, message: response }
                });
                return response;
            } catch (error) {
                console.error('Failed to send message:', error);
                throw error;
            }
        },
        setTyping: (userId, isTyping) => {
            dispatch({
                type: 'SET_TYPING',
                payload: { userId, isTyping }
            });
        },
        markAsRead: async (codeId, messageIds) => {
            try {
                await chatService.markAsRead(messageIds);
                dispatch({
                    type: 'MARK_AS_READ',
                    payload: { codeId }
                });
            } catch (error) {
                console.error('Failed to mark messages as read:', error);
            }
        }
    };

    return (
        <ChatContext.Provider value={value}>
            {children}
        </ChatContext.Provider>
    );
};

export const useChat = () => {
    const context = useContext(ChatContext);
    if (!context) {
        throw new Error('useChat must be used within a ChatProvider');
    }
    return context;
}; 