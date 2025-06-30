import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send } from 'lucide-react';

const ChatbotPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  useEffect(() => {
    setMessages([
      {
        text: "Olá! Eu sou o assistente virtual da BlauSight. Como posso te ajudar a analisar os desvios hoje?",
        sender: "bot"
      }
    ]);
  }, []);

  const handleSend = async () => {
    if (input.trim() === '') return;

    const userMessage = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Usa a mensagem de erro da API se disponível
        throw new Error(data.error || 'A resposta da rede não foi ok');
      }

      const botMessage = { text: data.reply, sender: 'bot' };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error("Erro ao contatar a API do chat:", error);
      // Exibe a mensagem de erro capturada
      const errorMessage = { text: `Desculpe, ocorreu um erro: ${error.message}`, sender: 'bot' };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] bg-gray-100 dark:bg-gray-900">
      <div className="flex-grow p-6 overflow-auto">
        <div className="flex flex-col space-y-4">
          {messages.map((msg, index) => (
            <div key={index} className={`flex items-end ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.sender === 'bot' && (
                <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white mr-3 flex-shrink-0">
                  <Bot size={24} />
                </div>
              )}
              <div
                className={`px-4 py-2 rounded-lg inline-block max-w-lg ${
                  msg.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200'
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
           <div ref={messagesEndRef} />
        </div>
      </div>
      <div className="p-4 bg-white border-t border-gray-200 dark:bg-gray-800 dark:border-gray-700">
        <div className="flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua mensagem..."
            className="flex-grow px-4 py-2 border rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
          <button
            onClick={handleSend}
            className="px-4 py-2 bg-blue-500 text-white rounded-r-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPage;