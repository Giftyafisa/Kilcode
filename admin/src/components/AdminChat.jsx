import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { wsManager } from '../utils/websocketManager';
import { toast } from 'react-hot-toast';

function AdminChat({ userId, codeId, onClose }) {
    const { user } = useAuth();
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        // Add WebSocket listeners for chat
        wsManager.addListener('CHAT_MESSAGE', handleNewMessage);
        wsManager.addListener('USER_TYPING', handleUserTyping);

        return () => {
            wsManager.removeListener('CHAT_MESSAGE', handleNewMessage);
            wsManager.removeListener('USER_TYPING', handleUserTyping);
        };
    }, []);

    const handleNewMessage = (data) => {
        if (data.codeId === codeId) {
            setMessages(prev => [...prev, data.message]);
            scrollToBottom();
        }
    };

    const handleUserTyping = (data) => {
        if (data.userId === userId) {
            // Show typing indicator
            // Implementation here
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const sendMessage = async () => {
        if (!newMessage.trim()) return;

        try {
            wsManager.socket.send(JSON.stringify({
                type: 'CHAT_MESSAGE',
                data: {
                    codeId,
                    userId,
                    message: newMessage,
                    adminId: user.id
                }
            }));

            setMessages(prev => [...prev, {
                text: newMessage,
                sender: 'admin',
                timestamp: new Date().toISOString()
            }]);
            
            setNewMessage('');
            scrollToBottom();
        } catch (error) {
            toast.error('Failed to send message');
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
                <div className="p-4 border-b flex justify-between items-center">
                    <h3 className="text-lg font-semibold">Chat with User</h3>
                    <button 
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        ×
                    </button>
                </div>

                <div className="h-96 overflow-y-auto p-4 space-y-4">
                    {messages.map((msg, index) => (
                        <div 
                            key={index}
                            className={`flex ${msg.sender === 'admin' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div className={`rounded-lg px-4 py-2 max-w-xs ${
                                msg.sender === 'admin' 
                                    ? 'bg-blue-500 text-white' 
                                    : 'bg-gray-100'
                            }`}>
                                <p>{msg.text}</p>
                                <span className="text-xs opacity-75">
                                    {new Date(msg.timestamp).toLocaleTimeString()}
                                </span>
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>

                <div className="p-4 border-t">
                    <div className="flex space-x-2">
                        <input
                            type="text"
                            value={newMessage}
                            onChange={(e) => setNewMessage(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                            placeholder="Type your message..."
                            className="flex-1 p-2 border rounded-lg"
                        />
                        <button
                            onClick={sendMessage}
                            disabled={loading}
                            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
                        >
                            Send
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default AdminChat; 