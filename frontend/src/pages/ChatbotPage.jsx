import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatbotPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    setMessages([
      {
        id: 'initial-message',
        text: "Olá! Eu sou o assistente virtual da BlauSight. Como posso te ajudar a analisar os desvios hoje?",
        sender: "bot"
      }
    ]);
  }, []);

  const handleSend = async () => {
    if (input.trim() === '' || isLoading) return;

    const userMessage = { id: `user-${Date.now()}`, text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    const botMessageId = `bot-${Date.now()}`;
    setMessages(prev => [...prev, { id: botMessageId, text: '', sender: 'bot' }]);

    try {
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`A resposta da rede não foi 'ok'. Status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        setMessages(prev => prev.map(msg => 
          msg.id === botMessageId 
            ? { ...msg, text: msg.text + chunk } 
            : msg
        ));
      }

    } catch (error) {
      console.error("Erro ao contatar a API do chat:", error);
      setMessages(prev => prev.map(msg => 
        msg.id === botMessageId
          ? { ...msg, text: `Desculpe, ocorreu um erro de conexão com o servidor.` }
          : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSend();
    }
  };

  // Componente para a mensagem do bot, agora com renderização de Markdown
  const BotMessage = ({ content, isLoading, isLastMessage }) => (
    <div className="prose prose-slate dark:prose-invert max-w-none">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
      {/* EFEITO DE DIGITAÇÃO: Adiciona um cursor pulsante se esta for a última mensagem e ainda estiver carregando */}
      {isLoading && isLastMessage && (
        <span className="inline-block w-2 h-5 bg-blue-500 animate-pulse ml-1 rounded-sm" />
      )}
    </div>
  );

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] bg-gray-100 dark:bg-gray-900">
      <div className="flex-grow p-6 overflow-auto">
        <div className="flex flex-col space-y-4">
          {messages.map((msg, index) => (
            <div key={msg.id} className={`flex items-end ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.sender === 'bot' && (
                <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white mr-3 flex-shrink-0">
                  <Bot size={24} />
                </div>
              )}
              <div
                className={`px-4 py-2 rounded-lg inline-block max-w-2xl break-words ${
                  msg.sender === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-200'
                }`}
              >
                {msg.sender === 'bot' ? (
                  <BotMessage 
                    content={msg.text} 
                    isLoading={isLoading}
                    isLastMessage={index === messages.length - 1} 
                  />
                ) : (
                  msg.text
                )}
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
            placeholder={isLoading ? "Aguarde a resposta..." : "Digite sua mensagem..."}
            className="flex-grow px-4 py-2 border rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            className="px-4 py-2 bg-blue-500 text-white rounded-r-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-300 dark:disabled:bg-slate-600 disabled:cursor-not-allowed"
            disabled={isLoading}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPage;