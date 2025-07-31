// Workspace manager component that handles module switching
import React, { useState } from 'react';
import { Dashboard } from '../Dashboard/Dashboard';
import { useAuth } from '../Auth/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import { Toggle } from '../UI/Toggle';
import { WorkflowEditor } from '../WorkflowEditor/WorkflowEditor';
import { WorkflowDashboard } from '../WorkflowEditor/WorkflowDashboard';
import { 
  SunIcon, 
  MoonIcon,
  BellIcon,
  Cog6ToothIcon 
} from '@heroicons/react/24/outline';

// Placeholder components for different modules
const ChatModule = () => (
  <div className="p-6">
    <h2 className="text-2xl font-bold text-gray-900 mb-4">Chat Module</h2>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <p className="text-gray-600">Chat interface will be implemented here.</p>
    </div>
  </div>
);

const DocumentModule = () => (
  <div className="p-6">
    <h2 className="text-2xl font-bold text-gray-900 mb-4">Document Management</h2>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <p className="text-gray-600">Document upload and management interface will be implemented here.</p>
    </div>
  </div>
);

const WorkflowModule = () => {
  const [workflowView, setWorkflowView] = useState<'dashboard' | 'editor'>('dashboard');

  if (workflowView === 'editor') {
    return (
      <div style={{ 
        height: 'calc(100vh - 64px)', // Trừ đi height của header
        width: '100%',
        overflow: 'hidden'
      }}>
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setWorkflowView('dashboard')}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            ← Back to Dashboard
          </button>
        </div>
        <WorkflowEditor 
          onBack={() => setWorkflowView('dashboard')}
        />
      </div>
    );
  }

  return (
    <div className="h-full">
      <WorkflowDashboard onOpenEditor={() => setWorkflowView('editor')} />
    </div>
  );
};

const MCPModule = () => (
  <div className="p-6">
    <h2 className="text-2xl font-bold text-gray-900 mb-4">MCP Plugins</h2>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <p className="text-gray-600">Model Context Protocol plugin management will be implemented here.</p>
    </div>
  </div>
);

const AnalyticsModule = () => (
  <div className="p-6">
    <h2 className="text-2xl font-bold text-gray-900 mb-4">Analytics</h2>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <p className="text-gray-600">Analytics and reporting dashboard will be implemented here.</p>
    </div>
  </div>
);

const TeamModule = () => (
  <div className="p-6">
    <h2 className="text-2xl font-bold text-gray-900 mb-4">Team Management</h2>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <p className="text-gray-600">Team collaboration and user management will be implemented here.</p>
    </div>
  </div>
);

const SettingsModule = () => (
  <div className="p-6">
    <h2 className="text-2xl font-bold text-gray-900 mb-4">Settings</h2>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <p className="text-gray-600">Application settings and configuration will be implemented here.</p>
    </div>
  </div>
);

export const WorkspaceManager: React.FC = () => {
  const [activeModule, setActiveModule] = useState('dashboard');
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();

  const renderModule = () => {
    switch (activeModule) {
      case 'dashboard':
        return <Dashboard user={user || undefined} onModuleChange={setActiveModule} />;
      case 'chat':
        return <ChatModule />;
      case 'documents':
      case 'upload':
      case 'manage':
        return <DocumentModule />;
      case 'workflows':
      case 'designer':
      case 'executions':
        return <WorkflowModule />;
      case 'mcp':
      case 'registry':
      case 'installed':
        return <MCPModule />;
      case 'analytics':
        return <AnalyticsModule />;
      case 'team':
        return <TeamModule />;
      case 'settings':
        return <SettingsModule />;
      default:
        return <Dashboard user={user || undefined} onModuleChange={setActiveModule} />;
    }
  };

  return (
    <div className={`min-h-screen flex transition-colors duration-300 ${
      isDark ? 'bg-gray-900' : 'bg-gray-50'
    }`}>
      {/* Sidebar */}
      <div className={`w-64 shadow-xl transition-colors duration-300 flex flex-col ${
        isDark 
          ? 'bg-gray-800 border-gray-700' 
          : 'bg-white border-gray-200'
      } border-r`}>
        {/* Logo */}
        <div className={`p-4 border-b transition-colors duration-300 ${
          isDark ? 'border-gray-700' : 'border-gray-200'
        }`}>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-sm">EC</span>
            </div>
            <h1 className={`text-lg font-semibold transition-colors duration-300 ${
              isDark ? 'text-gray-100' : 'text-gray-800'
            }`}>
              EmbeddedChat
            </h1>
          </div>
        </div>

        {/* Navigation - flex-1 để chiếm không gian có sẵn */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: '🏠' },
            { id: 'chat', label: 'Chat', icon: '💬' },
            { id: 'documents', label: 'Documents', icon: '📄' },
            { id: 'workflows', label: 'Workflows', icon: '⚡' },
            { id: 'mcp', label: 'MCP Plugins', icon: '🧩' },
            { id: 'analytics', label: 'Analytics', icon: '📊' },
            { id: 'team', label: 'Team', icon: '👥' },
            { id: 'settings', label: 'Settings', icon: '⚙️' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveModule(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2 text-left rounded-lg transition-all duration-200 hover:scale-105 ${
                activeModule === item.id
                  ? 'bg-blue-100 text-blue-700 shadow-md border-l-4 border-blue-700 dark:bg-blue-900 dark:text-blue-300'
                  : isDark 
                    ? 'text-gray-300 hover:bg-gray-700 hover:text-gray-100'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Theme Toggle và User info ở cuối sidebar - không dùng absolute */}
        <div className={`p-4 border-t transition-colors duration-300 ${
          isDark ? 'border-gray-700' : 'border-gray-200'
        }`}>
          {/* Theme Toggle */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              {isDark ? (
                <MoonIcon className="w-5 h-5 text-gray-400" />
              ) : (
                <SunIcon className="w-5 h-5 text-gray-600" />
              )}
              <span className={`text-sm font-medium ${
                isDark ? 'text-gray-300' : 'text-gray-700'
              }`}>
                {isDark ? 'Dark' : 'Light'} Mode
              </span>
            </div>
            <Toggle 
              enabled={isDark}
              onChange={toggleTheme}
              size="sm"
            />
          </div>

          {/* User info */}
          {user && (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-md">
                  <span className="text-sm font-medium text-white">
                    {user.username?.[0]?.toUpperCase()}
                  </span>
                </div>
                <div className="text-sm min-w-0 flex-1">
                  <div className={`font-medium transition-colors duration-300 truncate ${
                    isDark ? 'text-gray-100' : 'text-gray-800'
                  }`}>
                    {user.username}
                  </div>
                  <div className={`text-xs transition-colors duration-300 truncate ${
                    isDark ? 'text-gray-400' : 'text-gray-500'
                  }`}>
                    {user.email}
                  </div>
                </div>
              </div>
              <button
                onClick={logout}
                className={`p-2 rounded text-xs transition-all duration-200 hover:scale-110 flex-shrink-0 ${
                  isDark 
                    ? 'text-red-400 hover:bg-red-900/20' 
                    : 'text-red-600 hover:bg-red-50'
                }`}
                title="Logout"
              >
                🚪
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className={`shadow-sm border-b transition-colors duration-300 px-6 py-4 ${
          isDark 
            ? 'bg-gray-800 border-gray-700' 
            : 'bg-white border-gray-200'
        }`}>
          <div className="flex items-center justify-between">
            <h2 className={`text-xl font-semibold capitalize transition-colors duration-300 ${
              isDark ? 'text-gray-100' : 'text-gray-800'
            }`}>
              {activeModule === 'mcp' ? 'MCP Plugins' : activeModule}
            </h2>
            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <button className={`relative p-2 rounded-lg transition-all duration-200 hover:scale-110 ${
                isDark 
                  ? 'text-gray-400 hover:text-gray-200 hover:bg-gray-700' 
                  : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
              }`}>
                <BellIcon className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
              </button>

              {/* Settings */}
              <button className={`p-2 rounded-lg transition-all duration-200 hover:scale-110 ${
                isDark 
                  ? 'text-gray-400 hover:text-gray-200 hover:bg-gray-700' 
                  : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
              }`}>
                <Cog6ToothIcon className="w-5 h-5" />
              </button>

              <span className={`text-sm transition-colors duration-300 ${
                isDark ? 'text-gray-400' : 'text-gray-500'
              }`}>
                {new Date().toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className={`flex-1 ${activeModule === 'workflows' ? '' : 'overflow-auto'}`}>
          {renderModule()}
        </div>
      </div>
    </div>
  );
};
