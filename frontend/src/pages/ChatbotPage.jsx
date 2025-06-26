import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Bot, User, Send, LoaderCircle } from 'lucide-react';

const ChatbotPage = () => {
    const [messages, setMessages] = useState([
        { sender: 'bot', text: 'Olá! Sou o assistente de IA da BlauSight. Como posso ajudar você a analisar um desvio hoje?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const API_URL = 'http://localhost:8000/api';

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }

    useEffect(scrollToBottom, [messages]);

    const handleSend = async () => {
        if (input.trim() === '' || loading) return;

        const userMessage = { sender: 'user', text: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            // AINDA NÃO IMPLEMENTADO NO BACKEND
            // const response = await axios.post(`${API_URL}/chat`, { query: input });
            // const botResponse = { sender: 'bot', text: response.data.reply };
            
            // ---- RESPOSTA SIMULADA (REMOVER DEPOIS) ----
            await new Promise(res => setTimeout(res, 1500));
            const botResponse = { sender: 'bot', text: `Recebi sua mensagem: "${input}". A integração com o modelo de linguagem (Groq) ainda precisa ser feita no backend.`};
            // ---- FIM DA RESPOSTA SIMULADA ----

            setMessages(prev => [...prev, botResponse]);
        } catch (error) {
            const errorResponse = { sender: 'bot', text: 'Desculpe, não consegui me conectar ao meu cérebro. Tente novamente mais tarde.' };
            setMessages(prev => [...prev, errorResponse]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-10rem)] bg-white dark:bg-slate-800 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
            <div className="flex-1 p-6 overflow-y-auto">
                <div className="space-y-6">
                    {messages.map((msg, index) => (
                        <div key={index} className={`flex items-start gap-4 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                            {msg.sender === 'bot' && <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white"><Bot /></div>}
                            <div className={`p-4 rounded-2xl max-w-lg ${msg.sender === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-bl-none'}`}>
                                <p>{msg.text}</p>
                            </div>
                            {msg.sender === 'user' && <div className="flex-shrink-0 w-10 h-10 rounded-full bg-slate-300 dark:bg-slate-600 flex items-center justify-center text-slate-800 dark:text-slate-200"><User /></div>}
                        </div>
                    ))}
                     {loading && (
                        <div className="flex items-start gap-4">
                             <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white"><Bot /></div>
                             <div className="p-4 rounded-2xl max-w-lg bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-bl-none">
                                <LoaderCircle className="animate-spin" />
                             </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>
            <div className="p-4 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-b-2xl">
                <div className="relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Digite sua pergunta sobre o desvio..."
                        className="w-full p-4 pr-12 bg-slate-100 dark:bg-slate-700 border-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={loading}
                    />
                    <button onClick={handleSend} disabled={loading || !input.trim()} className="absolute inset-y-0 right-0 flex items-center justify-center w-12 text-slate-500 hover:text-blue-500 disabled:text-slate-400 disabled:cursor-not-allowed">
                        <Send />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatbotPage;