import React, { useState } from 'react';
import axios from 'axios';
import './ChatWidget.css'; // Add custom styling

const ChatWidget = () => {
    const [messages, setMessages] = useState([]);
    const [userMessage, setUserMessage] = useState('');

    const handleSendMessage = async () => {
        if (userMessage.trim() === '') return;

        const newMessage = { role: 'user', content: userMessage };
        setMessages([...messages, newMessage]);

        try {
            const response = await axios.post('http://127.0.0.1:5000/chat', { message: userMessage });
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
            <div className="chat-body">
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
