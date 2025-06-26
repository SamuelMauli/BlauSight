import React from 'react';
import { Menu } from 'lucide-react';

const Header = ({ sidebarOpen, setSidebarOpen, activePage }) => {
    const pageTitles = {
        analyze: 'Análise Preditiva de Causa Raiz',
        train: 'Treinamento do Modelo de IA',
        chatbot: 'Assistente de IA BlauSight'
    }
  return (
    <header className="flex items-center justify-between px-6 py-4 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
      <div className="flex items-center">
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-gray-500 focus:outline-none md:hidden">
          <Menu size={24} />
        </button>
        <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-200 ml-4 md:ml-0">{pageTitles[activePage]}</h2>
      </div>
    </header>
  );
};

export default Header;