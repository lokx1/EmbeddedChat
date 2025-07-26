// Workspace manager component that handles module switching
import React, { useState } from 'react';
import { Dashboard } from '../Dashboard/Dashboard';
import { useAuth } from '../Auth/AuthContext';

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

const WorkflowModule = () => (
  <div className="p-6">
    <h2 className="text-2xl font-bold text-gray-900 mb-4">Workflow Designer</h2>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <p className="text-gray-600">n8n-style workflow designer will be implemented here.</p>
    </div>
  </div>
);

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

  const renderModule = () => {
    switch (activeModule) {
      case 'dashboard':
        return <Dashboard onModuleChange={setActiveModule} />;
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
        return <Dashboard onModuleChange={setActiveModule} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 shadow-sm">
        {/* Logo */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">EC</span>
            </div>
            <h1 className="text-lg font-semibold text-gray-800">
              EmbeddedChat
            </h1>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
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
              className={`w-full flex items-center space-x-3 px-3 py-2 text-left rounded-lg transition-colors ${
                activeModule === item.id
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* User info at bottom */}
        {user && (
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-600">
                    {user.username?.[0]?.toUpperCase()}
                  </span>
                </div>
                <div className="text-sm">
                  <div className="font-medium text-gray-800">{user.username}</div>
                  <div className="text-gray-500 text-xs">{user.email}</div>
                </div>
              </div>
              <button
                onClick={logout}
                className="text-red-600 hover:bg-red-50 p-2 rounded text-xs"
                title="Logout"
              >
                🚪
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-800 capitalize">
              {activeModule === 'mcp' ? 'MCP Plugins' : activeModule}
            </h2>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
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
        <div className="flex-1 overflow-auto">
          {renderModule()}
        </div>
      </div>
    </div>
  );
};

export default WorkspaceManager;
