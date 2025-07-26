// Main layout wrapper
import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Dashboard } from '../Dashboard';
import { N8nChat } from '../Chat';

interface LayoutProps {
  children?: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isDark } = useTheme();
  const [activeModule, setActiveModule] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const renderMainContent = () => {
    switch (activeModule) {
      case 'dashboard':
        return <Dashboard onModuleChange={setActiveModule} />;
      case 'chat':
        return <N8nChat />;
      case 'documents':
        return (
          <div className={`p-8 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            <h2 className="text-2xl font-semibold mb-4">Documents</h2>
            <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>Document management coming soon...</p>
          </div>
        );
      case 'workflows':
        return (
          <div className={`p-8 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            <h2 className="text-2xl font-semibold mb-4">Workflows</h2>
            <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>Workflow designer coming soon...</p>
          </div>
        );
      case 'analytics':
        return (
          <div className={`p-8 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            <h2 className="text-2xl font-semibold mb-4">Analytics</h2>
            <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>Analytics dashboard coming soon...</p>
          </div>
        );
      case 'team':
        return (
          <div className={`p-8 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            <h2 className="text-2xl font-semibold mb-4">Team</h2>
            <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>Team management coming soon...</p>
          </div>
        );
      case 'settings':
        return (
          <div className={`p-8 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            <h2 className="text-2xl font-semibold mb-4">Settings</h2>
            <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>System settings coming soon...</p>
          </div>
        );
      default:
        return <Dashboard onModuleChange={setActiveModule} />;
    }
  };

  return (
    <div className={`min-h-screen flex ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        activeModule={activeModule}
        onModuleChange={setActiveModule}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />

        {/* Main Content */}
        <main className={`flex-1 overflow-auto ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
          {children || renderMainContent()}
        </main>
      </div>
    </div>
  );
};

export default Layout;
