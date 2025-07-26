import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { useDashboardData } from '../../hooks/useDashboardData';

// Simplified Layout with proper structure
const Layout: React.FC = () => {
  const { isDark, toggleTheme } = useTheme();
  const [activeModule, setActiveModule] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Fetch dashboard data
  const { data: dashboardData, loading: dashboardLoading, error: dashboardError } = useDashboardData();

  return (
    <div className={`min-h-screen ${isDark ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
      {/* Header */}
      <header className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-b h-16 flex items-center justify-between px-6`}>
        {/* Left side - Logo */}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">EC</span>
          </div>
          <h1 className={`text-xl font-semibold ${isDark ? 'text-white' : 'text-gray-800'}`}>
            EmbeddedChat
          </h1>
          <div className={`ml-4 px-3 py-1 rounded-lg text-sm ${isDark ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-600'}`}>
            Workspace: Main Workspace
          </div>
        </div>

        {/* Right side - Controls */}
        <div className="flex items-center space-x-4">
          {/* Dark Mode Toggle */}
          <button 
            onClick={toggleTheme}
            className={`p-2 rounded-lg ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'} transition-colors`}
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? '☀️' : '🌙'}
          </button>
          
          {/* Notifications */}
          <button className={`p-2 rounded-lg ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'} transition-colors relative`}>
            🔔
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
          </button>
          
          {/* Settings */}
          <button className={`p-2 rounded-lg ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'} transition-colors`}>
            ⚙️
          </button>
        </div>
      </header>

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Sidebar */}
        <aside className={`${sidebarCollapsed ? 'w-16' : 'w-64'} ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-r flex-shrink-0 transition-all duration-300 relative`}>
          {/* Sidebar Header với toggle */}
          <div className={`p-4 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'} flex items-center justify-between`}>
            {!sidebarCollapsed && (
              <span className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                Navigation
              </span>
            )}
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className={`p-1.5 rounded-lg ${isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-100 text-gray-500'} transition-colors`}
              title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {sidebarCollapsed ? '→' : '←'}
            </button>
          </div>

          {/* Navigation */}
          <nav className="p-4">
            <div className="space-y-1">
              {/* Main Modules */}
              {[
                { id: 'dashboard', label: 'Dashboard', icon: '📊', category: 'main' },
                { id: 'chat', label: 'Chat', icon: '💬', badge: 1, category: 'main' }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveModule(item.id)}
                  className={`w-full flex items-center space-x-3 p-3 rounded-lg text-left transition-colors relative
                    ${activeModule === item.id 
                      ? (isDark ? 'bg-blue-900 text-blue-300' : 'bg-blue-100 text-blue-700')
                      : (isDark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100')
                    }
                  `}
                >
                  <span className="text-lg">{item.icon}</span>
                  {!sidebarCollapsed && (
                    <>
                      <span className="flex-1 font-medium">{item.label}</span>
                      {item.badge && (
                        <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                </button>
              ))}

              {/* Documents Section */}
              {!sidebarCollapsed && (
                <div className="pt-4">
                  <h3 className={`text-xs font-semibold uppercase tracking-wider mb-2 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Documents
                  </h3>
                </div>
              )}
              {[
                { id: 'documents', label: 'All Documents', icon: '📄', category: 'docs' },
                { id: 'upload', label: 'Upload', icon: '📤', category: 'docs' },
                { id: 'manage', label: 'Manage', icon: '🗂️', category: 'docs' }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveModule(item.id)}
                  className={`w-full flex items-center space-x-3 p-2.5 rounded-lg text-left transition-colors
                    ${sidebarCollapsed ? 'justify-center' : ''}
                    ${activeModule === item.id 
                      ? (isDark ? 'bg-purple-900 text-purple-300' : 'bg-purple-100 text-purple-700')
                      : (isDark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100')
                    }
                  `}
                >
                  <span className={sidebarCollapsed ? 'text-lg' : 'text-base'}>{item.icon}</span>
                  {!sidebarCollapsed && <span className="text-sm">{item.label}</span>}
                </button>
              ))}

              {/* Workflows & Automation */}
              {!sidebarCollapsed && (
                <div className="pt-4">
                  <h3 className={`text-xs font-semibold uppercase tracking-wider mb-2 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Automation
                  </h3>
                </div>
              )}
              {[
                { id: 'workflows', label: 'Workflows', icon: '🔄', category: 'auto' },
                { id: 'mcp-plugins', label: 'MCP Plugins', icon: '🧩', badge: 'New', category: 'auto' },
                { id: 'registry', label: 'Plugin Registry', icon: '�', category: 'auto' },
                { id: 'installed', label: 'Installed', icon: '✅', category: 'auto' }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveModule(item.id)}
                  className={`w-full flex items-center space-x-3 p-2.5 rounded-lg text-left transition-colors
                    ${sidebarCollapsed ? 'justify-center' : ''}
                    ${activeModule === item.id 
                      ? (isDark ? 'bg-green-900 text-green-300' : 'bg-green-100 text-green-700')
                      : (isDark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100')
                    }
                  `}
                >
                  <span className={sidebarCollapsed ? 'text-lg' : 'text-base'}>{item.icon}</span>
                  {!sidebarCollapsed && (
                    <>
                      <span className="flex-1 text-sm">{item.label}</span>
                      {item.badge && (
                        <span className="bg-green-500 text-white text-xs rounded-full px-2 py-0.5">
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                </button>
              ))}

              {/* Analytics & Team */}
              {!sidebarCollapsed && (
                <div className="pt-4">
                  <h3 className={`text-xs font-semibold uppercase tracking-wider mb-2 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Management
                  </h3>
                </div>
              )}
              {[
                { id: 'analytics', label: 'Analytics', icon: '📈', category: 'mgmt' },
                { id: 'team', label: 'Team', icon: '👥', category: 'mgmt' },
                { id: 'settings', label: 'Settings', icon: '⚙️', category: 'mgmt' }
              ].map((item) => (
                <button
                  key={item.id}  
                  onClick={() => setActiveModule(item.id)}
                  className={`w-full flex items-center space-x-3 p-2.5 rounded-lg text-left transition-colors
                    ${sidebarCollapsed ? 'justify-center' : ''}
                    ${activeModule === item.id 
                      ? (isDark ? 'bg-orange-900 text-orange-300' : 'bg-orange-100 text-orange-700')
                      : (isDark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100')
                    }
                  `}
                >
                  <span className={sidebarCollapsed ? 'text-lg' : 'text-base'}>{item.icon}</span>
                  {!sidebarCollapsed && <span className="text-sm">{item.label}</span>}
                </button>
              ))}
            </div>
          </nav>

          {/* Footer */}
          {!sidebarCollapsed && (
            <div className={`absolute bottom-0 left-0 right-0 p-4 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
              <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                <div>Version 1.0.0</div>
                <div className="mt-1">© 2025 EmbeddedChat</div>
              </div>
            </div>
          )}
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-hidden">
          {activeModule === 'dashboard' && (
            <div className="p-8 h-full overflow-y-auto">
              <div className="mb-8">
                <h2 className="text-3xl font-bold mb-2">Dashboard</h2>
                <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                  Monitor your EmbeddedChat system performance and activity
                </p>
              </div>

              {dashboardLoading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3">Loading dashboard data...</span>
                </div>
              ) : dashboardError ? (
                <div className="bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 p-4 rounded-lg mb-8">
                  <p>⚠️ Failed to load dashboard data: {dashboardError}</p>
                  <p className="text-sm mt-1">Showing cached/fallback data</p>
                </div>
              ) : null}

              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {[
                  { 
                    title: 'Total Chats', 
                    value: dashboardData?.overview?.total_chats?.toString() || '742', 
                    icon: '💬', 
                    color: 'blue' 
                  },
                  { 
                    title: 'Active Users', 
                    value: dashboardData?.overview?.active_users?.toString() || '23', 
                    icon: '👥', 
                    color: 'green' 
                  },
                  { 
                    title: 'Documents', 
                    value: dashboardData?.overview?.total_documents?.toString() || '156', 
                    icon: '📄', 
                    color: 'purple' 
                  },
                  { 
                    title: 'System Status', 
                    value: dashboardData?.overview?.system_status || 'Healthy', 
                    icon: '✅', 
                    color: 'green' 
                  }
                ].map((stat) => (
                  <div key={stat.title} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                          {stat.title}
                        </p>
                        <p className="text-2xl font-bold">{stat.value}</p>
                      </div>
                      <span className="text-2xl">{stat.icon}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* System Overview */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Performance */}
                <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6`}>
                  <h3 className="text-lg font-semibold mb-4">System Performance</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Memory Usage</span>
                        <span>{dashboardData?.performance?.memory_usage?.percent || 67}%</span>
                      </div>
                      <div className={`w-full ${isDark ? 'bg-gray-700' : 'bg-gray-200'} rounded-full h-2`}>
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${dashboardData?.performance?.memory_usage?.percent || 67}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>CPU Usage</span>
                        <span>{dashboardData?.performance?.cpu_usage?.percent || 23}%</span>
                      </div>
                      <div className={`w-full ${isDark ? 'bg-gray-700' : 'bg-gray-200'} rounded-full h-2`}>
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${dashboardData?.performance?.cpu_usage?.percent || 23}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className={`pt-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
                      <div className="flex justify-between text-sm">
                        <span>Uptime</span>
                        <span className="font-medium">{dashboardData?.performance?.uptime || '2:34:15'}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Quick Actions */}
                <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6`}>
                  <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                  <div className="space-y-3">
                    {[
                      { title: 'Start New Chat', desc: 'Begin a conversation with AI', icon: '💬' },
                      { title: 'Upload Documents', desc: 'Add new documents to knowledge base', icon: '📄' },
                      { title: 'System Settings', desc: 'Configure AI providers and settings', icon: '⚙️' }
                    ].map((action) => (
                      <button
                        key={action.title}
                        onClick={() => {
                          if (action.title.includes('Chat')) setActiveModule('chat');
                          if (action.title.includes('Upload')) setActiveModule('upload');
                          if (action.title.includes('Settings')) setActiveModule('settings');
                        }}
                        className={`w-full text-left ${isDark ? 'bg-gray-700 hover:bg-gray-600 border-gray-600' : 'bg-gray-50 hover:bg-gray-100 border-gray-200'} border rounded-lg p-4 transition-colors`}
                      >
                        <div className="flex items-start space-x-3">
                          <span className="text-lg">{action.icon}</span>
                          <div>
                            <h4 className="font-medium">{action.title}</h4>
                            <p className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-500'}`}>
                              {action.desc}
                            </p>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              {dashboardData?.recent_activity && dashboardData.recent_activity.length > 0 && (
                <div className={`mt-8 ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6`}>
                  <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                  <div className="space-y-3">
                    {dashboardData.recent_activity.slice(0, 5).map((activity, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className={`mt-1 w-2 h-2 rounded-full ${
                          activity.type === 'message' ? 'bg-blue-500' :
                          activity.type === 'document' ? 'bg-green-500' :
                          'bg-purple-500'
                        }`}></div>
                        <div className="flex-1">
                          <p className="font-medium">{activity.action}</p>
                          <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                            {activity.details}
                          </p>
                          <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                            {activity.time}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Status Banner */}
              <div className={`mt-8 ${
                dashboardData?.overview?.system_status === 'Healthy' 
                  ? 'bg-green-100 dark:bg-green-900' 
                  : 'bg-red-100 dark:bg-red-900'
              } rounded-lg p-4`}>
                <div className="flex items-center">
                  <span className={`mr-2 ${
                    dashboardData?.overview?.system_status === 'Healthy'
                      ? 'text-green-600 dark:text-green-300'
                      : 'text-red-600 dark:text-red-300'
                  }`}>
                    {dashboardData?.overview?.system_status === 'Healthy' ? '✅' : '⚠️'}
                  </span>
                  <span className={`font-medium ${
                    dashboardData?.overview?.system_status === 'Healthy'
                      ? 'text-green-800 dark:text-green-200'
                      : 'text-red-800 dark:text-red-200'
                  }`}>
                    System Status: {dashboardData?.overview?.system_status || 'All systems operational'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {activeModule === 'chat' && (
            <div className="h-full flex flex-col">
              {/* Chat Header */}
              <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-b p-4 flex items-center justify-between`}>
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">🤖</span>
                  <div>
                    <h2 className="text-lg font-semibold">AI Assistant</h2>
                    <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      Ask me anything, and I'll help you with detailed thinking and memory.
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <select className={`px-3 py-2 rounded-lg border ${isDark ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                    <option>Llama 3.2 (ollama)</option>
                  </select>
                  <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                    Clear Chat
                  </button>
                </div>
              </div>

              {/* Chat Messages Area */}
              <div className="flex-1 p-6 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-4">🤖</div>
                  <h3 className="text-xl font-semibold mb-2">Start a conversation</h3>
                  <p className={`${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Ask me anything, and I'll help you with detailed thinking and memory.
                  </p>
                </div>
              </div>

              {/* Chat Input */}
              <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-t p-4`}>
                <div className="flex space-x-4">
                  <input
                    type="text"
                    placeholder="Type your message..."
                    className={`flex-1 px-4 py-3 rounded-lg border ${isDark ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-300 placeholder-gray-500'}`}
                  />
                  <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    Send
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* MCP Plugins Module */}
          {activeModule === 'mcp-plugins' && (
            <div className="p-8 h-full overflow-y-auto">
              <div className="mb-8">
                <h2 className="text-3xl font-bold mb-2">MCP Plugins</h2>
                <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                  Model Context Protocol plugins for extending AI capabilities
                </p>
              </div>

              {/* Plugin Categories */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {[
                  { name: 'AI Providers', count: 5, icon: '🤖', color: 'blue' },
                  { name: 'Data Sources', count: 8, icon: '📊', color: 'green' },
                  { name: 'Integrations', count: 12, icon: '🔗', color: 'purple' },
                  { name: 'Utilities', count: 6, icon: '🛠️', color: 'orange' },
                  { name: 'Custom', count: 3, icon: '⚡', color: 'red' },
                  { name: 'Community', count: 25, icon: '🌟', color: 'yellow' }
                ].map((category) => (
                  <div key={category.name} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6 hover:shadow-lg transition-shadow cursor-pointer`}>
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-2xl">{category.icon}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium bg-${category.color}-100 text-${category.color}-800`}>
                        {category.count} plugins
                      </span>
                    </div>
                    <h3 className="font-semibold mb-2">{category.name}</h3>
                    <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      Available plugins in this category
                    </p>
                  </div>
                ))}
              </div>

              {/* Featured Plugins */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold mb-4">Featured Plugins</h3>
                <div className="space-y-4">
                  {[
                    { name: 'OpenAI GPT-4', desc: 'Advanced language model with reasoning capabilities', status: 'Active', type: 'AI Provider' },
                    { name: 'Anthropic Claude', desc: 'Constitutional AI with safety focus', status: 'Available', type: 'AI Provider' },
                    { name: 'Web Scraper', desc: 'Extract data from web pages and APIs', status: 'Installed', type: 'Data Source' },
                    { name: 'Database Connector', desc: 'Connect to SQL and NoSQL databases', status: 'Available', type: 'Integration' }
                  ].map((plugin) => (
                    <div key={plugin.name} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-4 flex items-center justify-between`}>
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                          <span className="text-white font-bold">P</span>
                        </div>
                        <div>
                          <h4 className="font-medium">{plugin.name}</h4>
                          <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{plugin.desc}</p>
                          <span className={`inline-block mt-1 px-2 py-0.5 rounded-full text-xs ${isDark ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-600'}`}>
                            {plugin.type}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          plugin.status === 'Active' ? 'bg-green-100 text-green-800' :
                          plugin.status === 'Installed' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {plugin.status}
                        </span>
                        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
                          {plugin.status === 'Available' ? 'Install' : 'Configure'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button 
                  onClick={() => setActiveModule('registry')}
                  className={`${isDark ? 'bg-gray-800 border-gray-700 hover:bg-gray-700' : 'bg-white border-gray-200 hover:bg-gray-50'} border rounded-lg p-4 text-left transition-colors`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">�</span>
                    <div>
                      <h4 className="font-medium">Browse Registry</h4>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Discover new plugins</p>
                    </div>
                  </div>
                </button>
                
                <button 
                  onClick={() => setActiveModule('installed')}
                  className={`${isDark ? 'bg-gray-800 border-gray-700 hover:bg-gray-700' : 'bg-white border-gray-200 hover:bg-gray-50'} border rounded-lg p-4 text-left transition-colors`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">✅</span>
                    <div>
                      <h4 className="font-medium">Manage Installed</h4>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Configure your plugins</p>
                    </div>
                  </div>
                </button>

                <button className={`${isDark ? 'bg-gray-800 border-gray-700 hover:bg-gray-700' : 'bg-white border-gray-200 hover:bg-gray-50'} border rounded-lg p-4 text-left transition-colors`}>
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">➕</span>
                    <div>
                      <h4 className="font-medium">Create Plugin</h4>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Build custom MCP plugin</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          )}

          {/* Registry Module */}
          {activeModule === 'registry' && (
            <div className="p-8 h-full overflow-y-auto">
              <div className="mb-8 flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold mb-2">Plugin Registry</h2>
                  <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                    Browse and install MCP plugins from the community
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  <input
                    type="text"
                    placeholder="Search plugins..."
                    className={`px-4 py-2 rounded-lg border ${isDark ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-300 placeholder-gray-500'}`}
                  />
                  <select className={`px-3 py-2 rounded-lg border ${isDark ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                    <option>All Categories</option>
                    <option>AI Providers</option>
                    <option>Data Sources</option>
                    <option>Integrations</option>
                  </select>
                </div>
              </div>

              {/* Plugin Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[
                  { name: 'GitHub Integration', author: 'GitHub Inc.', desc: 'Access GitHub repositories and issues', downloads: '12.5k', rating: 4.8, category: 'Integration' },
                  { name: 'Slack Connector', author: 'Slack Team', desc: 'Send messages and manage Slack channels', downloads: '8.2k', rating: 4.6, category: 'Integration' },
                  { name: 'PostgreSQL Plugin', author: 'Community', desc: 'Query and manage PostgreSQL databases', downloads: '15.1k', rating: 4.9, category: 'Data Source' },
                  { name: 'Claude 3.5 Sonnet', author: 'Anthropic', desc: 'Latest Claude model with enhanced capabilities', downloads: '25.3k', rating: 4.9, category: 'AI Provider' },
                  { name: 'Web Search', author: 'Community', desc: 'Search the web and get real-time information', downloads: '18.7k', rating: 4.7, category: 'Utility' },
                  { name: 'Email Assistant', author: 'Community', desc: 'Send and manage emails through AI', downloads: '9.4k', rating: 4.5, category: 'Integration' }
                ].map((plugin) => (
                  <div key={plugin.name} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6 hover:shadow-lg transition-shadow`}>
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
                        <span className="text-white font-bold text-lg">P</span>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${isDark ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-600'}`}>
                        {plugin.category}
                      </span>
                    </div>
                    
                    <h3 className="font-semibold mb-1">{plugin.name}</h3>
                    <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'} mb-2`}>by {plugin.author}</p>
                    <p className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-600'} mb-4`}>{plugin.desc}</p>
                    
                    <div className="flex items-center justify-between text-sm mb-4">
                      <span className={`${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        ⭐ {plugin.rating} • 📥 {plugin.downloads}
                      </span>
                    </div>
                    
                    <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      Install Plugin
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Installed Plugins Module */}
          {activeModule === 'installed' && (
            <div className="p-8 h-full overflow-y-auto">
              <div className="mb-8">
                <h2 className="text-3xl font-bold mb-2">Installed Plugins</h2>
                <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                  Manage and configure your installed MCP plugins
                </p>
              </div>

              {/* Installed Plugins List */}
              <div className="space-y-4">
                {[
                  { name: 'OpenAI GPT-4', version: 'v1.2.3', status: 'Active', lastUsed: '2 minutes ago', usage: '156 calls today' },
                  { name: 'Anthropic Claude', version: 'v2.1.0', status: 'Active', lastUsed: '1 hour ago', usage: '43 calls today' },
                  { name: 'Web Scraper', version: 'v0.8.5', status: 'Inactive', lastUsed: '3 days ago', usage: '12 calls this week' },
                  { name: 'Database Connector', version: 'v1.0.1', status: 'Active', lastUsed: '5 minutes ago', usage: '89 calls today' }
                ].map((plugin) => (
                  <div key={plugin.name} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                          <span className="text-white font-bold">P</span>
                        </div>
                        <div>
                          <h3 className="font-semibold">{plugin.name}</h3>
                          <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                            Version {plugin.version} • {plugin.lastUsed}
                          </p>
                          <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                            {plugin.usage}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          plugin.status === 'Active' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {plugin.status}
                        </span>
                        
                        <div className="flex items-center space-x-2">
                          <button className={`px-3 py-1 rounded-lg text-sm ${isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} transition-colors`}>
                            Configure
                          </button>
                          <button className={`px-3 py-1 rounded-lg text-sm ${
                            plugin.status === 'Active'
                              ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                              : 'bg-green-600 hover:bg-green-700 text-white'
                          } transition-colors`}>
                            {plugin.status === 'Active' ? 'Disable' : 'Enable'}
                          </button>
                          <button className="px-3 py-1 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm">
                            Remove
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Documents Module */}
          {(activeModule === 'documents' || activeModule === 'upload' || activeModule === 'manage') && (
            <div className="h-full flex flex-col">
              <div className="flex-shrink-0 p-8 pb-0">
                <div className="mb-6">
                  <h2 className="text-3xl font-bold mb-2">
                    {activeModule === 'upload' ? 'Upload Documents' : 
                     activeModule === 'manage' ? 'Manage Documents' : 'Documents'}
                  </h2>
                  <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                    {activeModule === 'upload' ? 'Add new documents to your knowledge base' :
                     activeModule === 'manage' ? 'Organize and manage your document library' :
                     'Access and search your document knowledge base'}
                  </p>
                </div>
              </div>

              {activeModule === 'upload' && (
                <div className="flex-1 px-8 pb-8 overflow-y-auto">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Upload Area */}
                    <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border-2 border-dashed p-8 text-center`}>
                      <div className="text-6xl mb-4">📤</div>
                      <h3 className="text-xl font-semibold mb-2">Drop files here</h3>
                      <p className={`${isDark ? 'text-gray-400' : 'text-gray-500'} mb-4`}>
                        or click to browse your computer
                      </p>
                      <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                        Select Files
                      </button>
                      <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'} mt-4`}>
                        Supports: PDF, DOCX, TXT, MD, HTML
                      </p>
                    </div>

                    {/* Upload Settings */}
                    <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6`}>
                      <h3 className="text-lg font-semibold mb-4">Upload Settings</h3>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">Processing Mode</label>
                          <select className={`w-full px-3 py-2 rounded-lg border ${isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'}`}>
                            <option>Automatic Processing</option>
                            <option>Manual Review</option>
                            <option>Batch Processing</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Category</label>
                          <select className={`w-full px-3 py-2 rounded-lg border ${isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'}`}>
                            <option>General Knowledge</option>
                            <option>Technical Documentation</option>
                            <option>Business Documents</option>
                            <option>Personal Notes</option>
                          </select>
                        </div>
                        <div className="flex items-center space-x-2">
                          <input type="checkbox" id="extract-metadata" className="rounded" />
                          <label htmlFor="extract-metadata" className="text-sm">Extract metadata</label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <input type="checkbox" id="enable-search" className="rounded" defaultChecked />
                          <label htmlFor="enable-search" className="text-sm">Enable full-text search</label>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {(activeModule === 'documents' || activeModule === 'manage') && (
                <div className="flex-1 flex flex-col min-h-0">
                  {/* Document Stats */}
                  <div className="flex-shrink-0 px-8 pb-6">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                      {[
                        { label: 'Total Documents', value: '156', icon: '📄' },
                        { label: 'Storage Used', value: '2.4 GB', icon: '💾' },
                        { label: 'Indexed', value: '142', icon: '🔍' },
                        { label: 'Categories', value: '8', icon: '🗂️' }
                      ].map((stat) => (
                        <div key={stat.label} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-4`}>
                          <div className="flex items-center justify-between">
                            <div>
                              <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{stat.label}</p>
                              <p className="text-xl font-bold">{stat.value}</p>
                            </div>
                            <span className="text-2xl">{stat.icon}</span>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Search and Filter */}
                    <div className="flex items-center space-x-4">
                      <input
                        type="text"
                        placeholder="Search documents..."
                        className={`flex-1 px-4 py-2 rounded-lg border ${isDark ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-300 placeholder-gray-500'}`}
                      />
                      <select className={`px-3 py-2 rounded-lg border ${isDark ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                        <option>All Categories</option>
                        <option>Technical Docs</option>
                        <option>Business</option>
                        <option>Personal</option>
                      </select>
                      <button 
                        onClick={() => setActiveModule('upload')}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Upload New
                      </button>
                    </div>
                  </div>

                  {/* Documents List - Scrollable */}
                  <div className="flex-1 min-h-0 overflow-y-auto px-8 pb-8">
                    <div className="space-y-4">
                      {[
                        { name: 'API Documentation.pdf', size: '2.4 MB', uploaded: '2 days ago', category: 'Technical', status: 'Indexed' },
                        { name: 'Business Plan 2025.docx', size: '1.8 MB', uploaded: '1 week ago', category: 'Business', status: 'Indexed' },
                        { name: 'Meeting Notes.md', size: '45 KB', uploaded: '3 hours ago', category: 'Personal', status: 'Processing' },
                        { name: 'User Guide.html', size: '890 KB', uploaded: '5 days ago', category: 'Technical', status: 'Indexed' }
                      ].map((doc) => (
                        <div key={doc.name} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-4 flex items-center justify-between`}>
                          <div className="flex items-center space-x-4">
                            <div className="text-2xl">📄</div>
                            <div>
                              <h3 className="font-medium">{doc.name}</h3>
                              <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                                {doc.size} • {doc.uploaded} • {doc.category}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              doc.status === 'Indexed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {doc.status}
                            </span>
                            <button className={`px-3 py-1 rounded-lg text-sm ${isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} transition-colors`}>
                              View
                            </button>
                            <button className="px-3 py-1 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm">
                              Delete
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Analytics Module */}
          {activeModule === 'analytics' && (
            <div className="p-8 h-full overflow-y-auto">
              <div className="mb-8">
                <h2 className="text-3xl font-bold mb-2">Analytics</h2>
                <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                  Monitor system performance and usage patterns
                </p>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {[
                  { title: 'Total Requests', value: '12,847', change: '+15.3%', trend: 'up' },
                  { title: 'Avg Response Time', value: '1.2s', change: '-8.7%', trend: 'down' },
                  { title: 'Success Rate', value: '99.2%', change: '+0.1%', trend: 'up' },
                  { title: 'Active Plugins', value: '8', change: '+2', trend: 'up' }
                ].map((metric) => (
                  <div key={metric.title} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6`}>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                        {metric.title}
                      </h3>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        metric.trend === 'up' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {metric.change}
                      </span>
                    </div>
                    <p className="text-2xl font-bold">{metric.value}</p>
                  </div>
                ))}
              </div>

              {/* Charts Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Usage Chart */}
                <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6`}>
                  <h3 className="text-lg font-semibold mb-4">Usage Over Time</h3>
                  <div className="h-64 flex items-end justify-center space-x-2">
                    {[40, 65, 45, 80, 55, 75, 60, 90, 70, 85, 95, 88].map((height, i) => (
                      <div
                        key={i}
                        className="bg-blue-600 rounded-t-sm flex-1 transition-all hover:bg-blue-700"
                        style={{ height: `${height}%` }}
                      ></div>
                    ))}
                  </div>
                  <div className="flex justify-between mt-4 text-sm text-gray-500">
                    <span>Jan</span>
                    <span>Dec</span>
                  </div>
                </div>

                {/* Plugin Usage */}
                <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6`}>
                  <h3 className="text-lg font-semibold mb-4">Top Plugins by Usage</h3>
                  <div className="space-y-4">
                    {[
                      { name: 'OpenAI GPT-4', usage: 45, color: 'blue' },
                      { name: 'Anthropic Claude', usage: 35, color: 'purple' },
                      { name: 'Web Scraper', usage: 15, color: 'green' },
                      { name: 'Database Connector', usage: 5, color: 'orange' }
                    ].map((plugin) => (
                      <div key={plugin.name}>
                        <div className="flex justify-between text-sm mb-1">
                          <span>{plugin.name}</span>
                          <span>{plugin.usage}%</span>
                        </div>
                        <div className={`w-full ${isDark ? 'bg-gray-700' : 'bg-gray-200'} rounded-full h-2`}>
                          <div 
                            className={`bg-${plugin.color}-600 h-2 rounded-full transition-all`}
                            style={{ width: `${plugin.usage}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6`}>
                <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                <div className="space-y-4">
                  {[
                    { action: 'New plugin installed', details: 'GitHub Integration v1.2.0', time: '2 minutes ago', type: 'install' },
                    { action: 'High response time detected', details: 'Average 3.2s in last 10 minutes', time: '15 minutes ago', type: 'warning' },
                    { action: 'Document processing completed', details: '12 files processed successfully', time: '1 hour ago', type: 'success' },
                    { action: 'Plugin updated', details: 'Claude v2.1.0 → v2.1.1', time: '3 hours ago', type: 'update' }
                  ].map((activity, i) => (
                    <div key={i} className="flex items-start space-x-3">
                      <div className={`mt-1 w-2 h-2 rounded-full ${
                        activity.type === 'success' ? 'bg-green-500' :
                        activity.type === 'warning' ? 'bg-yellow-500' :
                        activity.type === 'install' ? 'bg-blue-500' :
                        'bg-purple-500'
                      }`}></div>
                      <div className="flex-1">
                        <p className="font-medium">{activity.action}</p>
                        <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                          {activity.details}
                        </p>
                        <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                          {activity.time}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Workflows Module */}
          {activeModule === 'workflows' && (
            <div className="p-8 h-full overflow-y-auto">
              <div className="mb-8 flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold mb-2">Workflows</h2>
                  <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                    Automate tasks with custom AI workflows
                  </p>
                </div>
                <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Create Workflow
                </button>
              </div>

              {/* Workflow Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                {[
                  { title: 'Active Workflows', value: '12', icon: '⚡' },
                  { title: 'Executions Today', value: '47', icon: '▶️' },
                  { title: 'Success Rate', value: '98.3%', icon: '✅' },
                  { title: 'Avg Duration', value: '2.4s', icon: '⏱️' }
                ].map((stat) => (
                  <div key={stat.title} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-4`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{stat.title}</p>
                        <p className="text-xl font-bold">{stat.value}</p>
                      </div>
                      <span className="text-2xl">{stat.icon}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Workflow Templates */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold mb-4">Workflow Templates</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {[
                    { name: 'Document Summarization', desc: 'Automatically summarize uploaded documents', icon: '📝', category: 'Processing' },
                    { name: 'Email Response', desc: 'Generate and send email responses based on context', icon: '📧', category: 'Communication' },
                    { name: 'Data Analysis', desc: 'Analyze datasets and generate insights', icon: '📊', category: 'Analytics' },
                    { name: 'Content Translation', desc: 'Translate content between multiple languages', icon: '🌐', category: 'Language' },
                    { name: 'Code Review', desc: 'Automated code review and suggestions', icon: '👨‍💻', category: 'Development' },
                    { name: 'Report Generation', desc: 'Generate periodic reports from data sources', icon: '📄', category: 'Reporting' }
                  ].map((template) => (
                    <div key={template.name} className={`${isDark ? 'bg-gray-800 border-gray-700 hover:bg-gray-750' : 'bg-white border-gray-200 hover:bg-gray-50'} rounded-lg border p-6 cursor-pointer transition-colors`}>
                      <div className="flex items-center justify-between mb-4">
                        <span className="text-3xl">{template.icon}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${isDark ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-600'}`}>
                          {template.category}
                        </span>
                      </div>
                      <h4 className="font-semibold mb-2">{template.name}</h4>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'} mb-4`}>
                        {template.desc}
                      </p>
                      <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                        Use Template
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Active Workflows */}
              <div>
                <h3 className="text-xl font-semibold mb-4">Active Workflows</h3>
                <div className="space-y-4">
                  {[
                    { name: 'Daily Report Generator', status: 'Running', lastRun: '2 hours ago', nextRun: 'in 22 hours', executions: 156 },
                    { name: 'Document Auto-Tagger', status: 'Paused', lastRun: '1 day ago', nextRun: 'Manual', executions: 89 },
                    { name: 'Email Sentiment Analysis', status: 'Running', lastRun: '15 minutes ago', nextRun: 'in 45 minutes', executions: 234 }
                  ].map((workflow) => (
                    <div key={workflow.name} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg border p-6`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold">W</span>
                          </div>
                          <div>
                            <h4 className="font-semibold">{workflow.name}</h4>
                            <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                              Last run: {workflow.lastRun} • Next: {workflow.nextRun}
                            </p>
                            <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                              {workflow.executions} total executions
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            workflow.status === 'Running' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {workflow.status}
                          </span>
                          <button className={`px-3 py-1 rounded-lg text-sm ${isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} transition-colors`}>
                            Edit
                          </button>
                          <button className={`px-3 py-1 rounded-lg text-sm ${
                            workflow.status === 'Running'
                              ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                              : 'bg-green-600 hover:bg-green-700 text-white'
                          } transition-colors`}>
                            {workflow.status === 'Running' ? 'Pause' : 'Resume'}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Settings and other modules fallback */}
          {!['dashboard', 'chat', 'mcp-plugins', 'registry', 'installed', 'documents', 'upload', 'manage', 'analytics', 'workflows'].includes(activeModule) && (
            <div className="p-8 h-full overflow-y-auto text-center">
              <div className="text-6xl mb-4">🚧</div>
              <h2 className="text-2xl font-semibold mb-4 capitalize">{activeModule}</h2>
              <p className={`${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                This module is coming soon...
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Layout;
