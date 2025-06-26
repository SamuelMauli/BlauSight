import React from 'react';
import { BrainCircuit, BotMessageSquare, UploadCloud, Sun, Moon, X } from 'lucide-react';

const NavItem = ({ icon, text, active, onClick }) => (
  <li>
    <a
      href="#"
      onClick={onClick}
      className={`flex items-center p-3 my-1 rounded-lg transition-colors ${active ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'}`}
    >
      {icon}
      <span className="ml-3 font-medium">{text}</span>
    </a>
  </li>
);

const ThemeToggle = ({ theme, setTheme }) => (
    <div className="flex justify-center items-center p-2 mt-4 bg-slate-200 dark:bg-slate-700 rounded-full">
        <button
            onClick={() => setTheme('light')}
            className={`p-2 rounded-full transition-colors ${theme === 'light' ? 'bg-blue-500 text-white' : 'text-slate-500'}`}
        >
            <Sun size={20} />
        </button>
        <button
            onClick={() => setTheme('dark')}
            className={`p-2 rounded-full transition-colors ${theme === 'dark' ? 'bg-blue-600 text-white' : 'text-slate-500'}`}
        >
            <Moon size={20} />
        </button>
    </div>
);

const Sidebar = ({ activePage, setActivePage, theme, setTheme, sidebarOpen, setSidebarOpen }) => {
  const navItems = [
    { id: 'analyze', text: 'Análise Preditiva', icon: <BrainCircuit size={20} /> },
    { id: 'train', text: 'Treinar Modelo', icon: <UploadCloud size={20} /> },
    { id: 'chatbot', text: 'Assistente IA', icon: <BotMessageSquare size={20} /> },
  ];

  return (
    <>
      <aside className={`fixed inset-y-0 left-0 z-30 w-64 bg-white dark:bg-slate-800 shadow-xl transform transition-transform duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:translate-x-0`}>
        <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
          <h1 className="text-2xl font-bold text-blue-600 dark:text-blue-400">BlauSight</h1>
           <button onClick={() => setSidebarOpen(false)} className="md:hidden text-slate-500 hover:text-slate-800 dark:hover:text-white">
              <X size={24} />
           </button>
        </div>
        <nav className="p-4">
          <ul>
            {navItems.map(item => (
              <NavItem
                key={item.id}
                icon={item.icon}
                text={item.text}
                active={activePage === item.id}
                onClick={(e) => {
                    e.preventDefault();
                    setActivePage(item.id);
                    setSidebarOpen(false);
                }}
              />
            ))}
          </ul>
        <div className="absolute bottom-4 left-4 right-4">
            <ThemeToggle theme={theme} setTheme={setTheme} />
        </div>
        </nav>
      </aside>
       {sidebarOpen && <div className="fixed inset-0 bg-black opacity-50 z-20 md:hidden" onClick={() => setSidebarOpen(false)}></div>}
    </>
  );
};

export default Sidebar;