import React, { useState } from 'react';
import axios from 'axios';
import './ChatWidget.css'; // Add custom styling
import { useEffect, useRef } from 'react';

const ChatWidget = () => {
    const [messages, setMessages] = useState([]);
    const [userMessage, setUserMessage] = useState('');

    const chatBodyRef = useRef(null);

    useEffect(() => {
        // Scroll to the bottom of the chat body when a new message is added
        if (chatBodyRef.current) {
            chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = async () => {
        if (userMessage.trim() === '') return;

        const newMessage = { role: 'user', content: userMessage };
        setMessages([...messages, newMessage]);
        setUserMessage('');

        try {
            const response = await axios.post('http://'+window.location.hostname+':5000/chat', { message: userMessage });
            const botMessage = response.data.message ? { role: 'assistant', content: response.data.message } : { role: 'assistant', content: 'Sorry, I did not understand your request.' };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } catch (error) {
            console.error('Error fetching chat response:', error);
            console.log(error)
            const errorMessage = { role: 'assistant', content: 'An error occurred while processing your request.' };
            setMessages((prevMessages) => [...prevMessages, errorMessage]);
        }

        setUserMessage(''); // Clear the input
    };

    return (
        <div className="chat-widget">
            <div className="chat-header">Doctors Chatbot</div>
            <div className="chat-body" ref={chatBodyRef}>
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.role}`}>
                        {msg.content}
                    </div>
                ))}
            </div>
            <div className="chat-footer">
                <input
                    type="text"
                    placeholder="Type your message..."
                    value={userMessage}
                    onChange={(e) => setUserMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                />
                <button onClick={handleSendMessage}>Send</button>
            </div>
        </div>
    );
};

export default ChatWidget;
