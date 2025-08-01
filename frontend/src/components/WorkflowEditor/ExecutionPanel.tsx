/**
 * Execution Panel for Real-time Workflow Monitoring
 */
import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { ExecutionStatus, ExecutionLog, ExecutionEvent } from '../../services/enhancedWorkflowEditorApi';

interface ExecutionPanelProps {
  executionStatus: ExecutionStatus | null;
  executionLogs: ExecutionLog[];
  executionEvents: ExecutionEvent[];
  onClose: () => void;
}

const ExecutionPanel: React.FC<ExecutionPanelProps> = ({
  executionStatus,
  executionLogs,
  executionEvents,
  onClose
}) => {
  const { isDark } = useTheme() || { isDark: false };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'text-blue-600 bg-blue-100';
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'cancelled':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className={`w-96 border-l flex flex-col ${
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
            className={`p-1 rounded ${
              isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Execution Status */}
        {executionStatus && (
          <div className="mt-3">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(executionStatus.status)}`}>
                {executionStatus.status.toUpperCase()}
              </span>
              {executionStatus.is_running && (
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-xs text-blue-600">Running</span>
                </div>
              )}
            </div>
            
            <div className={`mt-2 text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              {executionStatus.started_at && (
                <div>Started: {formatTimestamp(executionStatus.started_at)}</div>
              )}
              {executionStatus.completed_at && (
                <div>Completed: {formatTimestamp(executionStatus.completed_at)}</div>
              )}
              {executionStatus.error_message && (
                <div className="text-red-500 mt-1">Error: {executionStatus.error_message}</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className={`border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="flex">
          <button className={`px-4 py-2 text-sm font-medium border-b-2 ${
            isDark 
              ? 'text-blue-400 border-blue-400 bg-gray-700' 
              : 'text-blue-600 border-blue-600 bg-gray-50'
          }`}>
            Events ({executionEvents.length})
          </button>
          <button className={`px-4 py-2 text-sm font-medium ${
            isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-600 hover:text-gray-800'
          }`}>
            Logs ({executionLogs.length})
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {/* Events Tab */}
        <div className="p-4 space-y-3">
          {executionEvents.length === 0 ? (
            <div className={`text-center py-8 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
              <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <p>No events yet</p>
              <p className="text-xs mt-1">Execute the workflow to see real-time events</p>
            </div>
          ) : (
            executionEvents.map((event, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${
                  isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-sm font-medium ${
                    event.event_type.includes('failed') || event.event_type.includes('error')
                      ? 'text-red-500'
                      : event.event_type.includes('completed') || event.event_type.includes('success')
                      ? 'text-green-500'
                      : 'text-blue-500'
                  }`}>
                    {event.event_type.replace(/_/g, ' ').toUpperCase()}
                  </span>
                  <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    {formatTimestamp(event.timestamp)}
                  </span>
                </div>
                
                {Object.keys(event.data).length > 0 && (
                  <div className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                    <pre className="whitespace-pre-wrap font-mono">
                      {JSON.stringify(event.data, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Logs Tab (hidden for now, would be shown based on tab selection) */}
        <div className="hidden p-4 space-y-3">
          {executionLogs.length === 0 ? (
            <div className={`text-center py-8 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
              <p>No logs available</p>
            </div>
          ) : (
            executionLogs.map((log, index) => (
              <div
                key={log.id || index}
                className={`p-3 rounded-lg border ${
                  isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-sm font-medium ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                    {log.step_name}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs ${getStatusColor(log.status)}`}>
                    {log.status}
                  </span>
                </div>
                
                <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  {formatTimestamp(log.created_at)}
                  {log.execution_time_ms && (
                    <span className="ml-2">• {log.execution_time_ms}ms</span>
                  )}
                </div>
                
                {log.error_message && (
                  <div className="mt-2 text-xs text-red-500">
                    Error: {log.error_message}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer */}
      <div className={`p-3 border-t text-xs ${
        isDark ? 'border-gray-700 text-gray-400' : 'border-gray-200 text-gray-500'
      }`}>
        <div className="flex items-center justify-between">
          <span>Real-time updates</span>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Connected</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExecutionPanel;
