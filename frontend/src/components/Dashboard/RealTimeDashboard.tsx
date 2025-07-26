import React, { useState, useEffect, useCallback } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { dashboardService } from '../../services/dashboardService';
import {
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  CalendarDaysIcon,
  UserGroupIcon,
  ServerIcon,
  BoltIcon
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

interface ConversationStats {
  id: string;
  title: string;
  message_count: number;
  last_activity: string;
  duration_minutes?: number;
  ai_provider_used?: string;
  has_documents: boolean;
}

interface AIProviderStats {
  provider: string;
  status: string;
  total_requests: number;
  avg_response_time: number;
  success_rate: number;
  models_available: number;
  last_used?: string;
}

const RealTimeDashboard: React.FC = () => {
  const { isDark } = useTheme();
  const isDarkMode = isDark;
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activity, setActivity] = useState<ActivityData[]>([]);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [conversations, setConversations] = useState<ConversationStats[]>([]);
  const [aiProviders, setAiProviders] = useState<AIProviderStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [realTimeCleanup, setRealTimeCleanup] = useState<(() => void) | null>(null);

  // Fetch dashboard data
  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsData, activityData, healthData, conversationsData, aiProvidersData] = await Promise.all([
        dashboardService.getStats(30),
        dashboardService.getActivity(30),
        dashboardService.getSystemHealth(),
        dashboardService.getRecentConversations(10),
        dashboardService.getAIProviderStats()
      ]);

      setStats(statsData);
      setActivity(activityData.activity_data);
      setHealth(healthData);
      setConversations(conversationsData.conversations);
      setAiProviders(aiProvidersData.providers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  // Setup real-time updates
  useEffect(() => {
    fetchDashboardData();

    // Start real-time updates
    const startRealTime = async () => {
      try {
        const cleanup = await dashboardService.startRealTimeUpdates((data) => {
          if (data.type === 'stats') {
            setStats(data.data);
          } else if (data.type === 'activity') {
            setActivity(prev => [data.data, ...prev.slice(0, 29)]);
          } else if (data.type === 'health') {
            setHealth(data.data);
          } else if (data.type === 'conversations') {
            setConversations(data.data);
          } else if (data.type === 'ai_providers') {
            setAiProviders(data.data);
          }
        });
        setRealTimeCleanup(() => cleanup);
      } catch (error) {
        console.error('Failed to setup real-time updates:', error);
      }
    };

    startRealTime();

    // Cleanup on unmount
    return () => {
      if (realTimeCleanup) {
        realTimeCleanup();
      }
    };
  }, [fetchDashboardData]);

  // Auto-refresh every 30 seconds as fallback
  useEffect(() => {
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

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

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatPercentage = (percentage: number) => {
    return `${Math.round(percentage)}%`;
  };

  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  if (loading) {
    return (
      <div className={`min-h-screen ${isDarkMode ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-900'}`}>
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-lg">Loading dashboard...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen ${isDarkMode ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-900'}`}>
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline"> {error}</span>
            <button
              onClick={fetchDashboardData}
              className="mt-2 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      isDarkMode ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-900'
    }`}>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Real-Time Dashboard</h1>
          <p className={`${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Live system overview and analytics
          </p>
          <div className="mt-2 flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-500">Live updates active</span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className={`p-6 rounded-lg shadow-md ${
            isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
          }`}>
            <div className="flex items-center">
              <ChatBubbleLeftRightIcon className="w-8 h-8 text-blue-500 mr-3" />
              <div>
                <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                  Total Conversations
                </p>
                <p className="text-2xl font-bold">{formatNumber(stats?.total_conversations || 0)}</p>
                <p className="text-sm text-green-500">
                  +{stats?.active_conversations_today || 0} today
                </p>
              </div>
            </div>
          </div>

          <div className={`p-6 rounded-lg shadow-md ${
            isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
          }`}>
            <div className="flex items-center">
              <ChatBubbleLeftRightIcon className="w-8 h-8 text-green-500 mr-3" />
              <div>
                <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                  Total Messages
                </p>
                <p className="text-2xl font-bold">{formatNumber(stats?.total_messages || 0)}</p>
                <p className="text-sm text-green-500">
                  +{stats?.messages_today || 0} today
                </p>
              </div>
            </div>
          </div>

          <div className={`p-6 rounded-lg shadow-md ${
            isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
          }`}>
            <div className="flex items-center">
              <DocumentTextIcon className="w-8 h-8 text-purple-500 mr-3" />
              <div>
                <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                  Documents
                </p>
                <p className="text-2xl font-bold">{formatNumber(stats?.total_documents || 0)}</p>
                <p className="text-sm text-blue-500">
                  Avg: {stats?.avg_messages_per_conversation?.toFixed(1) || 0}/conv
                </p>
              </div>
            </div>
          </div>

          <div className={`p-6 rounded-lg shadow-md ${
            isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
          }`}>
            <div className="flex items-center">
              <UserGroupIcon className="w-8 h-8 text-orange-500 mr-3" />
              <div>
                <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                  Active Users
                </p>
                <p className="text-2xl font-bold">{formatNumber(stats?.total_users || 0)}</p>
                <p className="text-sm text-orange-500">
                  Most active: {stats?.most_active_day || 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* System Health & AI Providers */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* System Health */}
          <div className={`p-6 rounded-lg shadow-md ${
            isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
          }`}>
            <div className="flex items-center mb-4">
              <ServerIcon className="w-6 h-6 text-blue-500 mr-2" />
              <h3 className="text-lg font-semibold">System Health</h3>
              <div className="ml-auto">
                {getStatusIcon(health?.overall_status || 'unknown')}
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span>Database</span>
                <span className={getStatusColor(health?.components.database.status || 'unknown')}>
                  {health?.components.database.status || 'Unknown'}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span>Memory Usage</span>
                <span className={(health?.components.system_resources.memory_usage_percent || 0) > 80 ? 'text-red-500' : 'text-green-500'}>
                  {formatPercentage(health?.components.system_resources.memory_usage_percent || 0)}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span>CPU Usage</span>
                <span className={(health?.components.system_resources.cpu_usage_percent || 0) > 80 ? 'text-red-500' : 'text-green-500'}>
                  {formatPercentage(health?.components.system_resources.cpu_usage_percent || 0)}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span>Disk Usage</span>
                <span className={(health?.components.system_resources.disk_usage_percent || 0) > 90 ? 'text-red-500' : 'text-green-500'}>
                  {formatPercentage(health?.components.system_resources.disk_usage_percent || 0)}
                </span>
              </div>
            </div>
          </div>

          {/* AI Providers */}
          <div className={`p-6 rounded-lg shadow-md ${
            isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
          }`}>
            <div className="flex items-center mb-4">
              <BoltIcon className="w-6 h-6 text-yellow-500 mr-2" />
              <h3 className="text-lg font-semibold">AI Providers</h3>
            </div>
            
            <div className="space-y-4">
              {aiProviders.map((provider) => (
                <div key={provider.provider} className="border-l-4 border-blue-500 pl-4">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-medium capitalize">{provider.provider}</span>
                    <span className={getStatusColor(provider.status)}>
                      {provider.status}
                    </span>
                  </div>
                  <div className="text-sm space-y-1">
                    <div className="flex justify-between">
                      <span className={isDarkMode ? 'text-gray-400' : 'text-gray-600'}>
                        Requests:
                      </span>
                      <span>{formatNumber(provider.total_requests)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className={isDarkMode ? 'text-gray-400' : 'text-gray-600'}>
                        Avg Response:
                      </span>
                      <span>{provider.avg_response_time}ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span className={isDarkMode ? 'text-gray-400' : 'text-gray-600'}>
                        Success Rate:
                      </span>
                      <span className="text-green-500">{provider.success_rate}%</span>
                    </div>
                    {provider.last_used && (
                      <div className="flex justify-between">
                        <span className={isDarkMode ? 'text-gray-400' : 'text-gray-600'}>
                          Last Used:
                        </span>
                        <span>{formatRelativeTime(provider.last_used)}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Activity Chart & Recent Conversations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Activity Chart */}
          <div className={`p-6 rounded-lg shadow-md ${
            isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
          }`}>
            <div className="flex items-center mb-4">
              <ChartBarIcon className="w-6 h-6 text-green-500 mr-2" />
              <h3 className="text-lg font-semibold">Activity Overview</h3>
            </div>
            
            <div className="space-y-4">
              {activity.slice(0, 7).map((day) => (
                <div key={day.date} className="flex items-center space-x-4">
                  <div className="text-sm w-20">
                    {new Date(day.date).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric' 
                    })}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span className="text-sm">
                        {day.conversations} conversations
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm">
                        {day.messages} messages
                      </span>
                    </div>
                  </div>
                  <div className="text-right text-sm">
                    <div className="text-purple-500">
                      {day.documents_uploaded} docs
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Conversations */}
          <div className={`p-6 rounded-lg shadow-md ${
            isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
          }`}>
            <div className="flex items-center mb-4">
              <CalendarDaysIcon className="w-6 h-6 text-purple-500 mr-2" />
              <h3 className="text-lg font-semibold">Recent Conversations</h3>
            </div>
            
            <div className="space-y-3">
              {conversations.slice(0, 6).map((conv) => (
                <div key={conv.id} className={`p-3 rounded border ${
                  isDarkMode ? 'border-gray-700' : 'border-gray-200'
                }`}>
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium truncate mr-2">{conv.title}</h4>
                    <span className="text-xs text-blue-500 bg-blue-100 px-2 py-1 rounded">
                      {conv.ai_provider_used}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className={isDarkMode ? 'text-gray-400' : 'text-gray-600'}>
                      {conv.message_count} messages
                    </span>
                    <span className={isDarkMode ? 'text-gray-400' : 'text-gray-600'}>
                      {formatRelativeTime(conv.last_activity)}
                    </span>
                  </div>
                  {conv.has_documents && (
                    <div className="mt-1">
                      <span className="text-xs text-green-500 bg-green-100 px-2 py-1 rounded">
                        Has Documents
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeDashboard;
