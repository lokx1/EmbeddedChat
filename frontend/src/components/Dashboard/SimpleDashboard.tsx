import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import {
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowTrendingUpIcon,
  CalendarDaysIcon
} from '@heroicons/react/24/outline';

interface DashboardStats {
  total_conversations: number;
  total_messages: number;
  total_documents: number;
  total_users: number;
  active_conversations_today: number;
  messages_today: number;
  avg_messages_per_conversation: number;
  most_active_day: string;
  ai_providers_status: any;
}

interface ActivityData {
  date: string;
  conversations: number;
  messages: number;
  documents_uploaded: number;
}

interface SystemHealth {
  overall_status: string;
  components: {
    database: { status: string; error?: string };
    ai_service: any;
    system_resources: {
      memory_usage_percent: number;
      cpu_usage_percent: number;
      disk_usage_percent: number;
      status: string;
    };
  };
}

export const SimpleDashboard: React.FC = () => {
  const { isDark } = useTheme();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activity, setActivity] = useState<ActivityData[]>([]);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load dashboard stats
      const statsResponse = await fetch('/api/v1/dashboard/stats');
      const statsData = await statsResponse.json();
      
      // Load activity data (last 7 days)
      const activityResponse = await fetch('/api/v1/dashboard/activity?days=7');
      const activityData = await activityResponse.json();
      
      // Load system health
      const healthResponse = await fetch('/api/v1/dashboard/system-health');
      const healthData = await healthResponse.json();
      
      setStats(statsData);
      setActivity(activityData.activity_data || []);
      setHealth(healthData);
      setError(null);
      
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return 'text-green-500';
      case 'degraded':
      case 'warning':
        return 'text-yellow-500';
      case 'unhealthy':
      case 'error':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'degraded':
      case 'warning':
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />;
      case 'unhealthy':
      case 'error':
        return <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />;
      default:
        return <ClockIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className={`min-h-screen p-6 ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-12">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <span className={`text-lg ${isDark ? 'text-white' : 'text-gray-900'}`}>
                Loading dashboard...
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen p-6 ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-12">
            <div className={`text-center p-6 rounded-lg border ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
              <ExclamationTriangleIcon className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className={`text-lg font-medium mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                Dashboard Error
              </h3>
              <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                {error}
              </p>
              <button
                onClick={loadDashboardData}
                className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen p-6 ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                Dashboard
              </h1>
              <p className={`text-sm mt-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                System overview and real-time statistics
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={loadDashboardData}
                className={`px-4 py-2 rounded-md transition-colors ${
                  isDark
                    ? 'bg-gray-700 hover:bg-gray-600 text-white'
                    : 'bg-white hover:bg-gray-50 text-gray-900 border border-gray-300'
                }`}
              >
                Refresh
              </button>
              <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                Last updated: {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>

        {/* System Health Status */}
        {health && (
          <div className={`mb-6 p-4 rounded-lg border ${
            isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
          }`}>
            <div className="flex items-center justify-between mb-4">
              <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                System Health
              </h2>
              <div className="flex items-center gap-2">
                {getStatusIcon(health.overall_status)}
                <span className={`font-medium ${getStatusColor(health.overall_status)}`}>
                  {health.overall_status.toUpperCase()}
                </span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Database */}
              <div className={`p-3 rounded-md ${isDark ? 'bg-gray-750' : 'bg-gray-50'}`}>
                <div className="flex items-center gap-2 mb-2">
                  <DocumentTextIcon className="w-4 h-4" />
                  <span className={`text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    Database
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(health.components.database.status)}
                  <span className={`text-xs ${getStatusColor(health.components.database.status)}`}>
                    {health.components.database.status}
                  </span>
                </div>
                {health.components.database.error && (
                  <p className="text-xs text-red-500 mt-1">{health.components.database.error}</p>
                )}
              </div>

              {/* AI Service */}
              <div className={`p-3 rounded-md ${isDark ? 'bg-gray-750' : 'bg-gray-50'}`}>
                <div className="flex items-center gap-2 mb-2">
                  <ChartBarIcon className="w-4 h-4" />
                  <span className={`text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    AI Service
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(health.components.ai_service?.overall_status)}
                  <span className={`text-xs ${getStatusColor(health.components.ai_service?.overall_status)}`}>
                    {health.components.ai_service?.overall_status || 'Unknown'}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {Object.keys(health.components.ai_service?.providers || {}).length} providers
                </p>
              </div>

              {/* System Resources */}
              <div className={`p-3 rounded-md ${isDark ? 'bg-gray-750' : 'bg-gray-50'}`}>
                <div className="flex items-center gap-2 mb-2">
                  <ChartBarIcon className="w-4 h-4" />
                  <span className={`text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    Resources
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(health.components.system_resources.status)}
                  <span className={`text-xs ${getStatusColor(health.components.system_resources.status)}`}>
                    {health.components.system_resources.status}
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  <div>CPU: {health.components.system_resources.cpu_usage_percent.toFixed(1)}%</div>
                  <div>Memory: {health.components.system_resources.memory_usage_percent.toFixed(1)}%</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Total Conversations */}
            <div className={`p-6 rounded-lg border ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Total Conversations
                  </p>
                  <p className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    {stats.total_conversations.toLocaleString()}
                  </p>
                  <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                    {stats.active_conversations_today} active today
                  </p>
                </div>
                <ChatBubbleLeftRightIcon className="w-8 h-8 text-blue-500" />
              </div>
            </div>

            {/* Total Messages */}
            <div className={`p-6 rounded-lg border ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Total Messages
                  </p>
                  <p className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    {stats.total_messages.toLocaleString()}
                  </p>
                  <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                    {stats.messages_today} sent today
                  </p>
                </div>
                <ChatBubbleLeftRightIcon className="w-8 h-8 text-green-500" />
              </div>
            </div>

            {/* Total Documents */}
            <div className={`p-6 rounded-lg border ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Documents
                  </p>
                  <p className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    {stats.total_documents.toLocaleString()}
                  </p>
                  <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                    Uploaded files
                  </p>
                </div>
                <DocumentTextIcon className="w-8 h-8 text-purple-500" />
              </div>
            </div>

            {/* Average Messages */}
            <div className={`p-6 rounded-lg border ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Avg Messages/Conv
                  </p>
                  <p className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    {stats.avg_messages_per_conversation.toFixed(1)}
                  </p>
                  <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                    Most active: {stats.most_active_day}
                  </p>
                </div>
                <ArrowTrendingUpIcon className="w-8 h-8 text-orange-500" />
              </div>
            </div>
          </div>
        )}

        {/* Activity Chart */}
        {activity.length > 0 && (
          <div className={`p-6 rounded-lg border ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
            <div className="flex items-center justify-between mb-6">
              <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                Recent Activity (Last 7 Days)
              </h2>
              <CalendarDaysIcon className="w-5 h-5 text-gray-500" />
            </div>
            
            <div className="space-y-4">
              {activity.map((day) => (
                <div key={day.date} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                      {new Date(day.date).toLocaleDateString('en-US', { 
                        weekday: 'short', 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                      <ChatBubbleLeftRightIcon className="w-4 h-4 text-blue-500" />
                      <span className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                        {day.conversations}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <ChatBubbleLeftRightIcon className="w-4 h-4 text-green-500" />
                      <span className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                        {day.messages}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <DocumentTextIcon className="w-4 h-4 text-purple-500" />
                      <span className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                        {day.documents_uploaded}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SimpleDashboard;
