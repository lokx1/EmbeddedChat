// Main dashboard with real data integration
import React, { useState, useEffect } from 'react';
import {
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  PlayIcon,
  ChartBarIcon,
  UserGroupIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { Button } from '../UI/Button';
import { AnimatedCard } from '../UI/AnimatedCard';
import { useTheme } from '../../contexts/ThemeContext';
import { dashboardService, DashboardStats, RecentActivityItem } from '../../services/dashboardService';
import { useNotification } from '../UI/NotificationSystem';

interface DashboardProps {
  user?: {
    id: number;
    username: string;
    email: string;
  };
  onModuleChange?: (module: string) => void;
}

interface StatsCard {
  title: string;
  value: string | number;
  change: string;
  trend: 'up' | 'down' | 'neutral';
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  action: string;
}

// Remove unused constants and functions that are replaced by real data

// Remove unused mock data
// Using real data from backend now

export const Dashboard: React.FC<DashboardProps> = ({ user, onModuleChange = () => {} }) => {
  const { isDark } = useTheme();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activities, setActivities] = useState<RecentActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!user) {
        console.log('Dashboard: No user, setting loading to false');
        setLoading(false);
        return;
      }
      
      console.log('Dashboard: Fetching data for user:', user.username);
      setLoading(true);
      try {
        const [statsData, activityData] = await Promise.all([
          dashboardService.getDashboardStats(),
          dashboardService.getRecentActivity()
        ]);
        
        console.log('Dashboard: Got stats data:', statsData);
        console.log('Dashboard: Got activity data:', activityData);
        
        setStats(statsData);
        setActivities(activityData);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        // Set fallback data when API fails - ensure new user has some data to show
        const fallbackStats = {
          activeChats: 0,
          totalDocuments: 0,
          totalWorkflows: 0,
          teamMembers: 1, // At least the current user
          chatGrowth: '0%',
          documentGrowth: '0%',
          workflowGrowth: '0%',
          memberGrowth: '0%'
        };
        console.log('Dashboard: Using fallback data:', fallbackStats);
        setStats(fallbackStats);
        setActivities([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [user]); // Keep user dependency but don't block on it

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
  };

  const getStatsCards = (): StatsCard[] => {
    if (!stats) return [];
    
    return [
      {
        title: 'Active Chats',
        value: stats.activeChats,
        change: stats.chatGrowth || 'No data',
        trend: (stats.chatGrowth && stats.chatGrowth.includes('+')) ? 'up' : (stats.chatGrowth && stats.chatGrowth.includes('-')) ? 'down' : 'neutral',
        icon: ChatBubbleLeftRightIcon,
        color: 'blue'
      },
      {
        title: 'Documents',
        value: stats.totalDocuments,
        change: stats.documentGrowth || 'No data',
        trend: (stats.documentGrowth && stats.documentGrowth.includes('+')) ? 'up' : (stats.documentGrowth && stats.documentGrowth.includes('-')) ? 'down' : 'neutral',
        icon: DocumentTextIcon,
        color: 'green'
      },
      {
        title: 'Workflows',
        value: stats.totalWorkflows,
        change: stats.workflowGrowth || 'No data',
        trend: (stats.workflowGrowth && stats.workflowGrowth.includes('+')) ? 'up' : (stats.workflowGrowth && stats.workflowGrowth.includes('-')) ? 'down' : 'neutral',
        icon: PlayIcon,
        color: 'purple'
      },
      {
        title: 'Team Members',
        value: stats.teamMembers,
        change: stats.memberGrowth || 'No change',
        trend: (stats.memberGrowth && stats.memberGrowth.includes('+')) ? 'up' : (stats.memberGrowth && stats.memberGrowth.includes('-')) ? 'down' : 'neutral',
        icon: UserGroupIcon,
        color: 'orange'
      }
    ];
  };

  const quickActions: QuickAction[] = [
    {
      id: 'new-chat',
      title: 'Start New Chat',
      description: 'Begin a conversation with AI assistance',
      icon: ChatBubbleLeftRightIcon,
      color: 'blue',
      action: 'chat'
    },
    {
      id: 'upload-doc',
      title: 'Upload Document',
      description: 'Add new documents to your knowledge base',
      icon: DocumentTextIcon,
      color: 'green',
      action: 'upload'
    },
    {
      id: 'create-workflow',
      title: 'Create Workflow',
      description: 'Design automated processes',
      icon: PlayIcon,
      color: 'purple',
      action: 'designer'
    },
    {
      id: 'view-analytics',
      title: 'View Analytics',
      description: 'Check performance metrics and insights',
      icon: ChartBarIcon,
      color: 'indigo',
      action: 'analytics'
    }
  ];
  const { addNotification } = useNotification();

  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'bg-blue-500 text-blue-100',
      green: 'bg-green-500 text-green-100',
      purple: 'bg-purple-500 text-purple-100',
      orange: 'bg-orange-500 text-orange-100',
      indigo: 'bg-indigo-500 text-indigo-100'
    };
    return colors[color as keyof typeof colors] || 'bg-gray-500 text-gray-100';
  };

  // Remove unused function - using inline icons now

  const handleQuickAction = (action: string, title: string) => {
    addNotification({
      type: 'info',
      title: `Opening ${title}`,
      message: 'Redirecting to the selected module...',
      duration: 2000
    });
    onModuleChange(action);
  };

  // Show loading if no user
  if (!user) {
    return (
      <div className={`p-6 min-h-screen flex items-center justify-center transition-colors duration-300 ${
        isDark ? 'bg-gray-900' : 'bg-gray-50'
      }`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className={`mt-4 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>Loading user data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`p-6 space-y-6 min-h-screen transition-colors duration-300 ${
      isDark ? 'bg-gray-900' : 'bg-gray-50'
    }`}>
      {/* Welcome Section */}
      <AnimatedCard gradient className="p-6 text-white bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="animate-fade-in">
          <h1 className="text-2xl font-bold mb-2">
            Welcome back, {user?.username || 'User'}! 👋
          </h1>
          <p className="text-blue-100">
            Here's what's happening with your EmbeddedChat workspace today.
          </p>
        </div>
      </AnimatedCard>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {loading ? (
          // Loading skeleton
          Array.from({ length: 4 }).map((_, index) => (
            <AnimatedCard key={index} className="p-6 animate-pulse">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className={`h-4 rounded mb-2 ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
                  <div className={`h-8 rounded mb-2 ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
                  <div className={`h-4 rounded w-16 ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
                </div>
                <div className={`w-12 h-12 rounded-full ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
              </div>
            </AnimatedCard>
          ))
        ) : (
          getStatsCards().map((stat, index) => (
            <AnimatedCard 
              key={index} 
              className={`p-6 animate-slide-up`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${
                    isDark ? 'text-gray-400' : 'text-gray-600'
                  }`}>
                    {stat.title}
                  </p>
                  <p className={`text-2xl font-bold mt-1 ${
                    isDark ? 'text-gray-100' : 'text-gray-900'
                  }`}>
                    {stat.value}
                  </p>
                  <div className="flex items-center mt-2">
                    {stat.trend === 'up' && (
                      <ArrowTrendingUpIcon className="w-4 h-4 text-green-500 mr-1" />
                    )}
                    {stat.trend === 'down' && (
                      <ArrowTrendingDownIcon className="w-4 h-4 text-red-500 mr-1" />
                    )}
                    <span className={`text-sm ${
                      stat.trend === 'up' ? 'text-green-600' : 
                      stat.trend === 'down' ? 'text-red-600' : 'text-gray-500'
                    }`}>
                      {stat.change}
                    </span>
                  </div>
                </div>
                <div className={`p-3 rounded-full ${getColorClasses(stat.color)} animate-bounce-subtle`}>
                  <stat.icon className="w-6 h-6" />
                </div>
              </div>
            </AnimatedCard>
          ))
        )}
      </div>

      {/* Quick Actions */}
      <AnimatedCard className="animate-slide-up">
        <div className={`p-6 border-b ${
          isDark ? 'border-gray-700' : 'border-gray-200'
        }`}>
          <h2 className={`text-lg font-semibold ${
            isDark ? 'text-gray-100' : 'text-gray-900'
          }`}>
            Quick Actions
          </h2>
          <p className={`text-sm mt-1 ${
            isDark ? 'text-gray-400' : 'text-gray-600'
          }`}>
            Get started with common tasks
          </p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action) => (
              <div
                key={action.id}
                className={`group p-4 border rounded-lg transition-all cursor-pointer hover:scale-105 ${
                  isDark 
                    ? 'border-gray-600 hover:border-gray-500 hover:shadow-md' 
                    : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                }`}
                onClick={() => handleQuickAction(action.action, action.title)}
              >
                <div className={`inline-flex p-3 rounded-lg ${getColorClasses(action.color)} mb-3 group-hover:scale-110 transition-transform`}>
                  <action.icon className="w-6 h-6" />
                </div>
                <h3 className={`font-medium transition-colors ${
                  isDark 
                    ? 'text-gray-100 group-hover:text-blue-400' 
                    : 'text-gray-900 group-hover:text-blue-600'
                }`}>
                  {action.title}
                </h3>
                <p className={`text-sm mt-1 ${
                  isDark ? 'text-gray-400' : 'text-gray-600'
                }`}>
                  {action.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </AnimatedCard>

      {/* Recent Activity */}
      <AnimatedCard className="animate-slide-up">
        <div className={`p-6 border-b ${
          isDark ? 'border-gray-700' : 'border-gray-200'
        }`}>
          <h2 className={`text-lg font-semibold ${
            isDark ? 'text-gray-100' : 'text-gray-900'
          }`}>
            Recent Activity
          </h2>
          <p className={`text-sm mt-1 ${
            isDark ? 'text-gray-400' : 'text-gray-600'
          }`}>
            Latest updates from your workspace
          </p>
        </div>
        <div className={`divide-y ${
          isDark ? 'divide-gray-700' : 'divide-gray-200'
        }`}>
          {loading ? (
            // Loading skeleton for activities
            Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="p-6 animate-pulse">
                <div className="flex items-start space-x-3">
                  <div className={`w-5 h-5 rounded-full ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
                  <div className="flex-1 min-w-0">
                    <div className={`h-4 rounded mb-2 ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
                    <div className={`h-4 rounded mb-2 w-3/4 ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
                    <div className={`h-3 rounded w-20 ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
                  </div>
                </div>
              </div>
            ))
          ) : activities.length > 0 ? (
            activities.map((activity) => (
              <div 
                key={activity.id} 
                className={`p-6 transition-colors hover:${
                  isDark ? 'bg-gray-700' : 'bg-gray-50'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {activity.status === 'success' ? (
                      <CheckCircleIcon className="w-5 h-5 text-green-500" />
                    ) : activity.status === 'error' ? (
                      <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
                    ) : (
                      <ClockIcon className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-medium ${
                      isDark ? 'text-gray-100' : 'text-gray-900'
                    }`}>
                      {activity.title}
                    </p>
                    <p className={`text-sm mt-1 ${
                      isDark ? 'text-gray-400' : 'text-gray-600'
                    }`}>
                      {activity.description}
                    </p>
                    <p className={`text-xs mt-2 ${
                      isDark ? 'text-gray-500' : 'text-gray-500'
                    }`}>
                      {formatTimestamp(activity.timestamp)}
                    </p>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="p-6 text-center">
              <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                No recent activity to display
              </p>
            </div>
          )}
        </div>
        <div className={`p-6 border-t ${
          isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-gray-50'
        }`}>
          <Button 
            variant="ghost" 
            className="w-full justify-center"
            onClick={() => onModuleChange('analytics')}
          >
            View All Activity
          </Button>
        </div>
      </AnimatedCard>
    </div>
  );
};
