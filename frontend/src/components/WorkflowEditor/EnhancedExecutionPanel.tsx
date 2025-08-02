/**
 * Enhanced Execution Panel with Real Backend Integration
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { 
  WorkflowTaskLog, 
  WorkflowExecutionStep, 
  useEnhancedLogging 
} from '../../services/enhancedLoggingService';

interface EnhancedExecutionPanelProps {
  workflowInstanceId?: string;
  onClose: () => void;
  isVisible: boolean;
}

type TabType = 'events' | 'logs' | 'summary';

const EnhancedExecutionPanel: React.FC<EnhancedExecutionPanelProps> = ({
  workflowInstanceId,
  onClose,
  isVisible
}) => {
  const { isDark } = useTheme() || { isDark: false };
  const [activeTab, setActiveTab] = useState<TabType>('events');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Data states
  const [taskLogs, setTaskLogs] = useState<WorkflowTaskLog[]>([]);
  const [executionSteps, setExecutionSteps] = useState<WorkflowExecutionStep[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  
  // Service hooks
  const { 
    getTaskLogs, 
    getExecutionSteps
  } = useEnhancedLogging();

  // Load data
  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const [tasksResult, stepsResult] = await Promise.all([
        getTaskLogs({ 
          workflow_instance_id: workflowInstanceId,
          limit: 50 
        }),
        getExecutionSteps({ 
          workflow_instance_id: workflowInstanceId,
          limit: 50 
        })
      ]);

      if (tasksResult.success && tasksResult.data) {
        setTaskLogs(tasksResult.data);
      } else if (tasksResult.error) {
        console.warn('Failed to load task logs:', tasksResult.error);
      }

      if (stepsResult.success && stepsResult.data) {
        setExecutionSteps(stepsResult.data);
      } else if (stepsResult.error) {
        console.warn('Failed to load execution steps:', stepsResult.error);
      }

      setLastUpdate(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setIsLoading(false);
    }
  }, [workflowInstanceId, getTaskLogs, getExecutionSteps]);

  // Setup real-time updates
  useEffect(() => {
    if (!isVisible || !workflowInstanceId) return;

    // Initial load
    loadData();

    // No real-time subscription - data is loaded on-demand when workflow completes
    console.log(`EnhancedExecutionPanel setup for workflow: ${workflowInstanceId}`);

    // Cleanup
    return () => {
      console.log(`EnhancedExecutionPanel cleanup for workflow: ${workflowInstanceId}`);
    };
  }, [isVisible, workflowInstanceId, loadData]);

  // No auto-refresh - data is loaded only on-demand when workflow completes

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'success':
      case 'completed':
        return isDark ? 'text-green-400 bg-green-400/20' : 'text-green-600 bg-green-100';
      case 'failed':
      case 'error':
        return isDark ? 'text-red-400 bg-red-400/20' : 'text-red-600 bg-red-100';
      case 'running':
      case 'processing':
        return isDark ? 'text-blue-400 bg-blue-400/20' : 'text-blue-600 bg-blue-100';
      case 'pending':
        return isDark ? 'text-yellow-400 bg-yellow-400/20' : 'text-yellow-600 bg-yellow-100';
      default:
        return isDark ? 'text-gray-400 bg-gray-400/20' : 'text-gray-600 bg-gray-100';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return 'N/A';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  if (!isVisible) return null;

  return (
    <div className={`w-96 border-l flex flex-col h-full ${
      isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
    }`}>
      {/* Header */}
      <div className={`p-4 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="flex items-center justify-between">
          <h3 className={`font-semibold ${isDark ? 'text-gray-100' : 'text-gray-900'}`}>
            Execution Monitor
          </h3>
          <button
            onClick={onClose}
            className={`p-1 rounded hover:bg-opacity-20 ${
              isDark ? 'text-gray-400 hover:text-gray-200 hover:bg-gray-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Summary Stats */}
        <div className="mt-3 grid grid-cols-2 gap-2">
          <div className={`p-2 rounded ${isDark ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Task Logs</div>
            <div className={`text-sm font-semibold ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
              {taskLogs.length}
            </div>
          </div>
          <div className={`p-2 rounded ${isDark ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Execution Steps</div>
            <div className={`text-sm font-semibold ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
              {executionSteps.length}
            </div>
          </div>
        </div>

        {/* Connection Status */}
        <div className={`mt-2 flex items-center justify-between text-xs ${
          isDark ? 'text-gray-400' : 'text-gray-500'
        }`}>
          <span>Last update: {formatTimestamp(lastUpdate.toISOString())}</span>
          <div className="flex items-center gap-1">
            <div className={`w-2 h-2 rounded-full ${
              error ? 'bg-red-500' : 'bg-green-500 animate-pulse'
            }`}></div>
            <span>{error ? 'Disconnected' : 'Live'}</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className={`border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="flex">
          <button 
            onClick={() => setActiveTab('events')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'events'
                ? isDark 
                  ? 'text-blue-400 border-blue-400 bg-gray-700' 
                  : 'text-blue-600 border-blue-600 bg-gray-50'
                : isDark
                  ? 'text-gray-400 border-transparent hover:text-gray-200'
                  : 'text-gray-600 border-transparent hover:text-gray-800'
            }`}
          >
            Events ({executionSteps.length})
          </button>
          <button 
            onClick={() => setActiveTab('logs')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'logs'
                ? isDark 
                  ? 'text-blue-400 border-blue-400 bg-gray-700' 
                  : 'text-blue-600 border-blue-600 bg-gray-50'
                : isDark
                  ? 'text-gray-400 border-transparent hover:text-gray-200'
                  : 'text-gray-600 border-transparent hover:text-gray-800'
            }`}
          >
            Logs ({taskLogs.length})
          </button>
          <button 
            onClick={() => setActiveTab('summary')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'summary'
                ? isDark 
                  ? 'text-blue-400 border-blue-400 bg-gray-700' 
                  : 'text-blue-600 border-blue-600 bg-gray-50'
                : isDark
                  ? 'text-gray-400 border-transparent hover:text-gray-200'
                  : 'text-gray-600 border-transparent hover:text-gray-800'
            }`}
          >
            Summary
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center p-8">
            <div className={`animate-spin rounded-full h-8 w-8 border-b-2 ${
              isDark ? 'border-blue-400' : 'border-blue-600'
            }`}></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-4">
            <div className={`p-3 rounded-lg ${isDark ? 'bg-red-900/20 text-red-400' : 'bg-red-50 text-red-600'}`}>
              <div className="font-medium">Connection Error</div>
              <div className="text-sm mt-1">{error}</div>
              <button 
                onClick={loadData}
                className="text-sm underline mt-2 hover:no-underline"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Events Tab */}
        {activeTab === 'events' && !isLoading && !error && (
          <div className="p-4 space-y-3">
            {executionSteps.length === 0 ? (
              <div className={`text-center py-8 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p>No events yet</p>
                <p className="text-xs mt-1">Execute the workflow to see real-time events</p>
              </div>
            ) : (
              executionSteps.map((step) => (
                <div
                  key={step.id}
                  className={`p-3 rounded-lg border ${
                    isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-sm font-medium ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                      {step.step_name}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(step.status)}`}>
                      {step.status.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    {step.started_at && (
                      <div>Started: {formatTimestamp(step.started_at)}</div>
                    )}
                    {step.completed_at && (
                      <div>Completed: {formatTimestamp(step.completed_at)} • {formatDuration(step.execution_time_ms)}</div>
                    )}
                    {step.error_message && (
                      <div className="text-red-500 mt-1">Error: {step.error_message}</div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && !isLoading && !error && (
          <div className="p-4 space-y-3">
            {taskLogs.length === 0 ? (
              <div className={`text-center py-8 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                <p>No logs available</p>
              </div>
            ) : (
              taskLogs.map((log) => (
                <div
                  key={log.id}
                  className={`p-3 rounded-lg border ${
                    isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-sm font-medium ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                      {log.task_name}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(log.status || 'unknown')}`}>
                      {log.status?.toUpperCase() || 'UNKNOWN'}
                    </span>
                  </div>
                  
                  <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    {formatTimestamp(log.created_at)}
                    {log.execution_time_ms && (
                      <span className="ml-2">• {formatDuration(log.execution_time_ms)}</span>
                    )}
                    {log.log_level && (
                      <span className="ml-2">• {log.log_level.toUpperCase()}</span>
                    )}
                  </div>
                  
                  {log.failure_reason && (
                    <div className="mt-2 text-xs text-red-500">
                      Error: {log.failure_reason}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Summary Tab */}
        {activeTab === 'summary' && !isLoading && !error && (
          <div className="p-4 space-y-4">
            <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <h4 className={`font-medium mb-2 ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                Overall Statistics
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className={isDark ? 'text-gray-400' : 'text-gray-600'}>Total Task Logs:</span>
                  <span className={isDark ? 'text-gray-200' : 'text-gray-800'}>{taskLogs.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className={isDark ? 'text-gray-400' : 'text-gray-600'}>Total Steps:</span>
                  <span className={isDark ? 'text-gray-200' : 'text-gray-800'}>{executionSteps.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className={isDark ? 'text-gray-400' : 'text-gray-600'}>System Status:</span>
                  <span className={`px-2 py-1 rounded text-xs bg-green-100 text-green-800`}>
                    ACTIVE
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer with Refresh Button */}
      <div className={`p-3 border-t flex items-center justify-between text-xs ${
        isDark ? 'border-gray-700 text-gray-400' : 'border-gray-200 text-gray-500'
      }`}>
        <span>Manual refresh only - no auto-polling</span>
        <button
          onClick={loadData}
          disabled={isLoading}
          className={`px-2 py-1 rounded text-xs hover:bg-opacity-20 ${
            isDark ? 'text-blue-400 hover:bg-blue-400' : 'text-blue-600 hover:bg-blue-600'
          } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isLoading ? 'Loading...' : 'Refresh Now'}
        </button>
      </div>
    </div>
  );
};

export default EnhancedExecutionPanel;
