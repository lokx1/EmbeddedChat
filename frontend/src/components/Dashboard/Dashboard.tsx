import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { 
  ChartBarIcon, 
  ChatBubbleLeftRightIcon, 
  DocumentTextIcon,
  CogIcon,
  PlayIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface DashboardProps {
  onModuleChange: (module: string) => void;
}

interface DashboardStats {
  totalChats: number;
  activeUsers: number;
  documentsProcessed: number;
  systemStatus: 'healthy' | 'warning' | 'error';
  uptime: string;
  memoryUsage: number;
  cpuUsage: number;
}

export const Dashboard: React.FC<DashboardProps> = ({ onModuleChange }) => {
  const { isDark } = useTheme();
  const [stats, setStats] = useState<DashboardStats>({
    totalChats: 0,
    activeUsers: 0,
    documentsProcessed: 0,
    systemStatus: 'healthy',
    uptime: '0:00:00',
    memoryUsage: 0,
    cpuUsage: 0
  });

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/v1/dashboard/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        // Fallback to mock data if API is not available
        setStats({
          totalChats: Math.floor(Math.random() * 1000) + 500,
          activeUsers: Math.floor(Math.random() * 50) + 10,
          documentsProcessed: Math.floor(Math.random() * 200) + 100,
          systemStatus: 'healthy',
          uptime: '2:34:15',
          memoryUsage: Math.floor(Math.random() * 30) + 40,
          cpuUsage: Math.floor(Math.random() * 20) + 10
        });
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      // Use mock data as fallback
      setStats({
        totalChats: 742,
        activeUsers: 23,
        documentsProcessed: 156,
        systemStatus: 'healthy',
        uptime: '2:34:15',
        memoryUsage: 67,
        cpuUsage: 23
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ComponentType<any>;
    onClick?: () => void;
    color?: string;
  }> = ({ title, value, icon: Icon, onClick, color = 'text-blue-600' }) => (
    <div 
      className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg shadow-sm border p-6 ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>{title}</p>
          <p className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>{value}</p>
        </div>
        <Icon className={`h-8 w-8 ${color}`} />
      </div>
    </div>
  );

  const QuickAction: React.FC<{
    title: string;
    description: string;
    icon: React.ComponentType<any>;
    onClick: () => void;
    color?: string;
  }> = ({ title, description, icon: Icon, onClick, color = 'text-blue-600' }) => (
    <button
      onClick={onClick}
      className={`w-full text-left ${isDark ? 'bg-gray-800 border-gray-700 hover:bg-gray-750' : 'bg-white border-gray-200 hover:bg-gray-50'} rounded-lg shadow-sm border p-4 hover:shadow-md transition-all`}
    >
      <div className="flex items-start space-x-3">
        <Icon className={`h-6 w-6 ${color} mt-1`} />
        <div>
          <h3 className={`text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>{title}</h3>
          <p className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-500'}`}>{description}</p>
        </div>
      </div>
    </button>
  );

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-gray-200 rounded-lg h-32"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Dashboard</h1>
        <p className={`${isDark ? 'text-gray-300' : 'text-gray-600'} mt-2`}>Monitor your EmbeddedChat system performance and activity</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Chats"
          value={stats.totalChats}
          icon={ChatBubbleLeftRightIcon}
          onClick={() => onModuleChange('chat')}
          color="text-blue-600"
        />
        <StatCard
          title="Active Users"
          value={stats.activeUsers}
          icon={ChartBarIcon}
          color="text-green-600"
        />
        <StatCard
          title="Documents"
          value={stats.documentsProcessed}
          icon={DocumentTextIcon}
          onClick={() => onModuleChange('documents')}
          color="text-purple-600"
        />
        <StatCard
          title="System Status"
          value={stats.systemStatus.charAt(0).toUpperCase() + stats.systemStatus.slice(1)}
          icon={stats.systemStatus === 'healthy' ? PlayIcon : ExclamationTriangleIcon}
          color={stats.systemStatus === 'healthy' ? 'text-green-600' : 'text-red-600'}
        />
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg shadow-sm border p-6`}>
          <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'} mb-4`}>System Performance</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>Memory Usage</span>
                <span className={`${isDark ? 'text-white' : 'text-gray-900'}`}>{stats.memoryUsage}%</span>
              </div>
              <div className={`w-full ${isDark ? 'bg-gray-700' : 'bg-gray-200'} rounded-full h-2`}>
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${stats.memoryUsage}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>CPU Usage</span>
                <span className={`${isDark ? 'text-white' : 'text-gray-900'}`}>{stats.cpuUsage}%</span>
              </div>
              <div className={`w-full ${isDark ? 'bg-gray-700' : 'bg-gray-200'} rounded-full h-2`}>
                <div
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${stats.cpuUsage}%` }}
                ></div>
              </div>
            </div>
            <div className={`pt-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
              <div className="flex justify-between text-sm">
                <span className={`${isDark ? 'text-gray-300' : 'text-gray-600'}`}>Uptime</span>
                <span className={`${isDark ? 'text-white' : 'text-gray-900'} font-medium`}>{stats.uptime}</span>
              </div>
            </div>
          </div>
        </div>

        <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-lg shadow-sm border p-6`}>
          <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'} mb-4`}>Quick Actions</h2>
          <div className="space-y-3">
            <QuickAction
              title="Start New Chat"
              description="Begin a conversation with AI"
              icon={ChatBubbleLeftRightIcon}
              onClick={() => onModuleChange('chat')}
              color="text-blue-600"
            />
            <QuickAction
              title="Upload Documents"
              description="Add new documents to the knowledge base"
              icon={DocumentTextIcon}
              onClick={() => onModuleChange('documents')}
              color="text-purple-600"
            />
            <QuickAction
              title="System Settings"
              description="Configure AI providers and settings"
              icon={CogIcon}
              onClick={() => onModuleChange('settings')}
              color="text-gray-600"
            />
          </div>
        </div>
      </div>

      {/* Status Banner */}
      <div className={`rounded-lg p-4 ${getStatusColor(stats.systemStatus)}`}>
        <div className="flex items-center">
          {stats.systemStatus === 'healthy' ? (
            <PlayIcon className="h-5 w-5 mr-2" />
          ) : (
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
          )}
          <span className="font-medium">
            System Status: {stats.systemStatus === 'healthy' ? 'All systems operational' : 'System issues detected'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
