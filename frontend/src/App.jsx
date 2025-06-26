import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import AnalyzePage from './pages/AnalyzePage';
import TrainPage from './pages/TrainPage';
import ChatbotPage from './pages/ChatbotPage';

function App() {
  const [activePage, setActivePage] = useState('analyze');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove(theme === 'light' ? 'dark' : 'light');
    root.classList.add(theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const renderPage = () => {
    switch (activePage) {
      case 'train':
        return <TrainPage />;
      case 'chatbot':
        return <ChatbotPage />;
      case 'analyze':
      default:
        return <AnalyzePage />;
    }
  };

  return (
    <div className="flex h-screen bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-200">
      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
        theme={theme}
        setTheme={setTheme}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} activePage={activePage} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-100 dark:bg-slate-900">
          <div className="container mx-auto px-6 py-8">
            {renderPage()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;