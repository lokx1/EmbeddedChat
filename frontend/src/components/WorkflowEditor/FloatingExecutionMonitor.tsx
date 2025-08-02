/**
 * Floating Execution Monitor Button
 */
import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { useExecutionMonitor } from '../../hooks/useExecutionMonitor';

interface FloatingExecutionMonitorProps {
  className?: string;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
}

const FloatingExecutionMonitor: React.FC<FloatingExecutionMonitorProps> = ({
  className = '',
  position = 'bottom-right'
}) => {
  const { isDark } = useTheme() || { isDark: false };
  const {
    isVisible,
    isConnected,
    hasNewActivity,
    recentLogs,
    togglePanel,
    getActivityCount
  } = useExecutionMonitor();

  const getPositionClasses = () => {
    switch (position) {
      case 'bottom-left':
        return 'bottom-6 left-6';
      case 'top-right':
        return 'top-6 right-6';
      case 'top-left':
        return 'top-6 left-6';
      default:
        return 'bottom-6 right-6';
    }
  };

  const activityCount = getActivityCount();
  const hasActivity = activityCount > 0 || hasNewActivity;

  return (
    <div className={`fixed ${getPositionClasses()} z-50 ${className}`}>
      {/* Main Monitor Button */}
      <button
        onClick={togglePanel}
        className={`relative group flex items-center justify-center w-14 h-14 rounded-full shadow-xl transition-all duration-300 hover:scale-110 focus:outline-none focus:ring-4 ${
          isDark 
            ? 'bg-gray-800 hover:bg-gray-700 border border-gray-600 focus:ring-gray-500/50' 
            : 'bg-white hover:bg-gray-50 border border-gray-200 focus:ring-blue-500/50'
        } ${isVisible ? 'ring-4 ring-blue-500/30' : ''}`}
        title="Execution Monitor"
      >
        {/* Monitor Icon */}
        <svg 
          className={`w-6 h-6 transition-colors ${
            isConnected 
              ? isDark ? 'text-blue-400' : 'text-blue-600'
              : isDark ? 'text-gray-500' : 'text-gray-400'
          }`} 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" 
          />
        </svg>

        {/* Connection Status Indicator */}
        <div className={`absolute -top-1 -right-1 w-4 h-4 rounded-full border-2 ${
          isDark ? 'border-gray-800' : 'border-white'
        } ${
          isConnected 
            ? 'bg-green-500 animate-pulse' 
            : 'bg-red-500'
        }`} />

        {/* Activity Badge */}
        {hasActivity && (
          <div className={`absolute -top-2 -left-2 min-w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
            hasNewActivity
              ? 'bg-red-500 text-white animate-bounce'
              : isDark
                ? 'bg-blue-500 text-white'
                : 'bg-blue-600 text-white'
          } ${activityCount > 99 ? 'text-xs' : ''}`}>
            {activityCount > 99 ? '99+' : activityCount || '!'}
          </div>
        )}

        {/* Hover Tooltip */}
        <div className={`absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 px-3 py-2 rounded-lg text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap ${
          isDark 
            ? 'bg-gray-700 text-gray-200 border border-gray-600' 
            : 'bg-gray-900 text-white'
        }`}>
          <div className="text-center">
            <div>Execution Monitor</div>
            <div className="text-xs opacity-75 mt-1">
              {recentLogs.length} recent logs
            </div>
            <div className={`text-xs ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
          
          {/* Tooltip Arrow */}
          <div className={`absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent ${
            isDark ? 'border-t-gray-700' : 'border-t-gray-900'
          }`} />
        </div>
      </button>

      {/* Quick Stats Panel (shown when not expanded) */}
      {!isVisible && hasActivity && (
        <div className={`absolute bottom-full mb-4 right-0 w-64 p-3 rounded-lg shadow-xl border transition-all duration-300 ${
          isDark 
            ? 'bg-gray-800 border-gray-600 text-gray-200' 
            : 'bg-white border-gray-200 text-gray-800'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-sm">Recent Activity</h4>
            <button
              onClick={togglePanel}
              className={`text-xs px-2 py-1 rounded hover:bg-opacity-20 ${
                isDark ? 'text-blue-400 hover:bg-blue-400' : 'text-blue-600 hover:bg-blue-600'
              }`}
            >
              View All
            </button>
          </div>
          
          {recentLogs.slice(0, 3).map((log, index) => (
            <div key={`${log.id}-${index}`} className={`text-xs p-2 rounded mb-1 last:mb-0 ${
              isDark ? 'bg-gray-700' : 'bg-gray-50'
            }`}>
              <div className="flex items-center justify-between">
                <span className="font-medium truncate">
                  {'task_name' in log ? log.task_name : log.step_name}
                </span>
                <span className={`px-1 py-0.5 rounded text-xs ${
                  ('status' in log && log.status === 'success') || log.status === 'completed'
                    ? isDark ? 'text-green-400 bg-green-400/20' : 'text-green-600 bg-green-100'
                    : ('status' in log && log.status === 'failed') || log.status === 'failed'
                      ? isDark ? 'text-red-400 bg-red-400/20' : 'text-red-600 bg-red-100'
                      : isDark ? 'text-blue-400 bg-blue-400/20' : 'text-blue-600 bg-blue-100'
                }`}>
                  {('status' in log ? log.status : log.status)?.toUpperCase() || 'UNKNOWN'}
                </span>
              </div>
              <div className={`${isDark ? 'text-gray-400' : 'text-gray-500'} truncate`}>
                {new Date(log.created_at).toLocaleTimeString()}
              </div>
            </div>
          ))}
          
          {recentLogs.length > 3 && (
            <div className={`text-center text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'} mt-2`}>
              +{recentLogs.length - 3} more activities
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FloatingExecutionMonitor;
