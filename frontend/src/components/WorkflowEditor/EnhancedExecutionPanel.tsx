/**
 * Enhanced Execution Panel with Persistent Storage
 * Provides persistent storage for Events and Logs across page reloads
 */
import React, { useState, useMemo, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { ExecutionStatus, ExecutionLog, ExecutionEvent } from '../../services/enhancedWorkflowEditorApi';
import { useExecutionStorage } from '../../hooks/useExecutionStorage';
import { debugLocalStorage } from '../../utils/debugStorage';
import EmailReportPanel from './EmailReportPanel';

interface EnhancedExecutionPanelProps {
  executionStatus: ExecutionStatus | null;
  executionLogs: ExecutionLog[];
  executionEvents: ExecutionEvent[];
  instanceId?: string;
  workflowName?: string;
  onClose?: () => void;
}

// Enhanced interfaces for better data organization
interface ProcessedEvent {
  id: string;
  type: 'node_execution' | 'workflow_step' | 'data_processing' | 'system_event';
  title: string;
  content: Record<string, any>;
  timestamp: string;
  status: 'running' | 'completed' | 'failed' | 'pending';
  nodeId?: string;
  executionTime?: number;
}

interface ProcessedLog {
  id: string;
  level: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  nodeId?: string;
  executionTime?: number;
  details?: Record<string, any>;
}

const EnhancedExecutionPanel: React.FC<EnhancedExecutionPanelProps> = ({
  executionStatus: propExecutionStatus,
  executionLogs: propExecutionLogs = [],
  executionEvents: propExecutionEvents = [],
  instanceId,
  workflowName,
  onClose
}) => {
  const { isDark } = useTheme() || { isDark: false };
  const [activeTab, setActiveTab] = useState<'events' | 'logs'>('events');
  const [showStorageManager, setShowStorageManager] = useState(false);
  const [showEmailReport, setShowEmailReport] = useState(false);

  // Use the enhanced storage hook
  const {
    executionStatus: storedStatus,
    executionLogs: storedLogs,
    executionEvents: storedEvents,
    saveExecution,
    getRecentExecutions,
    clearAllExecutions,
    exportExecution,
    exportAllExecutions,
    getStorageStats,
    isLoading,
    error
  } = useExecutionStorage(instanceId, {
    autoSave: true,
    retentionDays: 7,
    maxStoredInstances: 50
  });

  // Smart merge: Use props data when available, fallback to stored data
  // Priority: Fresh props > Stored data > Recent execution > Empty state
  const effectiveStatus = propExecutionStatus || storedStatus;
  const effectiveLogs = propExecutionLogs.length > 0 ? propExecutionLogs : storedLogs;
  const effectiveEvents = propExecutionEvents.length > 0 ? propExecutionEvents : storedEvents;

  // Auto-load most recent execution when no valid data is available
  const [autoLoadedExecution, setAutoLoadedExecution] = useState<any>(null);
  const [hasAttemptedAutoLoad, setHasAttemptedAutoLoad] = useState(false);
  
  useEffect(() => {
    // Auto-load conditions:
    // 1. No instanceId provided OR instanceId exists but no stored data for it
    // 2. No props data available
    // 3. Haven't attempted auto-load yet OR data sources have changed
    
    const hasPropsData = propExecutionLogs.length > 0 || propExecutionEvents.length > 0 || propExecutionStatus;
    const hasStoredData = storedLogs.length > 0 || storedEvents.length > 0 || storedStatus;
    
    const shouldAutoLoad = !hasPropsData && !hasStoredData && !hasAttemptedAutoLoad;
    
    if (shouldAutoLoad) {
      console.log('🔍 Attempting auto-load - no valid data available');
      const recentExecutions = getRecentExecutions(1);
      
      if (recentExecutions.length > 0) {
        const mostRecent = recentExecutions[0];
        setAutoLoadedExecution(mostRecent);
        console.log('🔄 Auto-loaded most recent execution:', mostRecent.instanceId, {
          logs: mostRecent.executionLogs.length,
          events: mostRecent.executionEvents.length
        });
      } else {
        console.log('📭 No recent executions found to auto-load');
      }
      
      setHasAttemptedAutoLoad(true);
    }
    
    // Reset auto-load attempt when we get valid data
    if (hasPropsData || hasStoredData) {
      if (hasAttemptedAutoLoad) {
        console.log('📥 Valid data received, clearing auto-load state');
        setAutoLoadedExecution(null);
        setHasAttemptedAutoLoad(false);
      }
    }
  }, [instanceId, storedLogs.length, storedEvents.length, storedStatus, 
      propExecutionLogs.length, propExecutionEvents.length, propExecutionStatus,
      hasAttemptedAutoLoad, getRecentExecutions]);
  
  // Reset auto-load when instanceId changes from undefined to a specific value
  useEffect(() => {
    if (instanceId && autoLoadedExecution) {
      console.log('🔄 InstanceId set, clearing auto-loaded data to load specific instance');
      setAutoLoadedExecution(null);
      setHasAttemptedAutoLoad(false);
    }
  }, [instanceId, autoLoadedExecution]);

  // Use auto-loaded data when no other data is available  
  const finalStatus = effectiveStatus || autoLoadedExecution?.executionStatus;
  const finalLogs = effectiveLogs.length > 0 ? effectiveLogs : (autoLoadedExecution?.executionLogs || []);
  const finalEvents = effectiveEvents.length > 0 ? effectiveEvents : (autoLoadedExecution?.executionEvents || []);

  // Debug: Log whenever effective data changes
  useEffect(() => {
    console.log('📊 Data merge:', {
      instanceId: instanceId || 'none',
      autoLoadedId: autoLoadedExecution?.instanceId || 'none',
      sources: {
        status: propExecutionStatus ? 'props' : storedStatus ? 'stored' : autoLoadedExecution?.executionStatus ? 'auto-loaded' : 'none',
        logs: propExecutionLogs.length > 0 ? 'props' : storedLogs.length > 0 ? 'stored' : finalLogs.length > 0 ? 'auto-loaded' : 'none', 
        events: propExecutionEvents.length > 0 ? 'props' : storedEvents.length > 0 ? 'stored' : finalEvents.length > 0 ? 'auto-loaded' : 'none'
      },
      counts: {
        logs: finalLogs.length,
        events: finalEvents.length
      }
    });
  }, [instanceId, propExecutionStatus, propExecutionLogs, propExecutionEvents, 
      storedStatus, storedLogs, storedEvents, autoLoadedExecution, finalLogs, finalEvents]);

  // Auto-save when props change OR when final data changes
  useEffect(() => {
    if (instanceId && (finalStatus || finalLogs.length > 0 || finalEvents.length > 0)) {
      console.log('💾 Auto-saving execution data:', {
        instanceId: instanceId.slice(0, 8) + '...',
        status: finalStatus?.status,
        logsCount: finalLogs.length,
        eventsCount: finalEvents.length,
        source: 'comprehensive'
      });
      
      saveExecution(instanceId, finalStatus, finalLogs, finalEvents, workflowName);
    }
  }, [instanceId, finalStatus, finalLogs, finalEvents, workflowName, saveExecution]);

  // Also save when props change (for immediate data)
  useEffect(() => {
    if (instanceId && (propExecutionStatus || propExecutionLogs.length > 0 || propExecutionEvents.length > 0)) {
      console.log('💾 Auto-saving props data:', {
        instanceId: instanceId.slice(0, 8) + '...',
        status: propExecutionStatus?.status,
        logsCount: propExecutionLogs.length,
        eventsCount: propExecutionEvents.length,
        source: 'props'
      });
      
      saveExecution(instanceId, propExecutionStatus, propExecutionLogs, propExecutionEvents, workflowName);
    }
  }, [instanceId, propExecutionStatus, propExecutionLogs, propExecutionEvents, workflowName, saveExecution]);

  // Debug effect - log storage state when instanceId changes
  useEffect(() => {
    if (instanceId) {
      console.log('🔍 EnhancedExecutionPanel Debug for instance:', instanceId);
      console.log('Props data:', {
        propStatus: !!propExecutionStatus,
        propLogsCount: propExecutionLogs.length,
        propEventsCount: propExecutionEvents.length
      });
      console.log('Stored data:', {
        storedStatus: !!storedStatus,
        storedLogsCount: storedLogs.length,
        storedEventsCount: storedEvents.length
      });
      console.log('Effective data:', {
        finalStatus: !!finalStatus,
        finalLogsCount: finalLogs.length,
        finalEventsCount: finalEvents.length
      });
      
      // Call debug helper
      debugLocalStorage();
    }
  }, [instanceId, propExecutionStatus, propExecutionLogs, propExecutionEvents, 
      storedStatus, storedLogs, storedEvents, autoLoadedExecution, finalStatus, finalLogs, finalEvents]);

  // Process events - Transform raw execution events into concise summary events
  const processedEvents = useMemo((): ProcessedEvent[] => {
    const events: ProcessedEvent[] = [];
    const safeExecutionEvents = finalEvents || [];

    // Process raw execution events
    safeExecutionEvents.forEach((event: ExecutionEvent, index: number) => {
      if (event.data && typeof event.data === 'object') {
        // Check if this is a node execution completion with output data
        if (event.event_type === 'execution_completed' && event.data.output_data) {
          const outputData = event.data.output_data;
          
          // Process node outputs from the execution result
          if (outputData.node_outputs) {
            Object.entries(outputData.node_outputs).forEach(([nodeId, nodeOutput]: [string, any]) => {
              // Extract SUMMARY content for events (concise info only)
              const content: Record<string, any> = {};
              
              // Only show counts and basic stats for events
              if (nodeOutput.sheets_data && Array.isArray(nodeOutput.sheets_data)) {
                content.rows_processed = nodeOutput.sheets_data.length;
              }
              
              if (nodeOutput.values && Array.isArray(nodeOutput.values)) {
                content.input_count = nodeOutput.values.length;
              }
              
              if (nodeOutput.processed_results && Array.isArray(nodeOutput.processed_results)) {
                content.results_generated = nodeOutput.processed_results.length;
              }
              
              // Add operation type
              if (nodeOutput.operation) {
                content.operation = nodeOutput.operation;
              }
              
              // Add metadata summary if available
              if (nodeOutput.metadata) {
                content.model = nodeOutput.metadata.model;
                content.processing_time = nodeOutput.metadata.processing_time;
              }
              
              events.push({
                id: `${index}-${nodeId}`,
                type: 'node_execution',
                title: `${nodeId} Completed`,
                content,
                timestamp: event.timestamp,
                status: nodeOutput.error ? 'failed' : 'completed',
                nodeId,
                executionTime: nodeOutput.execution_time_ms
              });
            });
          }
        } 
        // Handle other event types with concise info
        else if (event.event_type.includes('started')) {
          events.push({
            id: `${index}-start`,
            type: 'workflow_step',
            title: 'Workflow Started',
            content: { instance_id: event.data.instance_id?.slice(0, 8) || 'Unknown' },
            timestamp: event.timestamp,
            status: 'running'
          });
        }
        else if (event.event_type.includes('step') || event.event_type.includes('node')) {
          events.push({
            id: `${index}-step`,
            type: 'data_processing',
            title: event.event_type.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            content: { step: event.event_type },
            timestamp: event.timestamp,
            status: event.event_type.includes('failed') ? 'failed' : 'completed'
          });
        }
        else {
          // Generic system event with minimal info
          events.push({
            id: `${index}-system`,
            type: 'system_event',
            title: event.event_type.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            content: { type: event.event_type },
            timestamp: event.timestamp,
            status: event.event_type.includes('failed') || event.event_type.includes('error') ? 'failed' : 'completed'
          });
        }
      }
    });

    return events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [finalEvents]);

  // Process logs - Transform execution logs into detailed logs with full content
  const processedLogs = useMemo((): ProcessedLog[] => {
    const logs: ProcessedLog[] = [];
    const safeExecutionLogs = finalLogs || [];
    const safeExecutionEvents = effectiveEvents || [];

    // Process execution events for DETAILED logs content
    safeExecutionEvents.forEach((event: ExecutionEvent, index: number) => {
      if (event.data && typeof event.data === 'object') {
        // Create detailed logs from execution completion events
        if (event.event_type === 'execution_completed' && event.data.output_data) {
          const outputData = event.data.output_data;
          
          if (outputData.node_outputs) {
            Object.entries(outputData.node_outputs).forEach(([nodeId, nodeOutput]: [string, any]) => {
              // Create detailed log with FULL content for inspection
              const fullDetails: Record<string, any> = {
                node_id: nodeId,
                operation: nodeOutput.operation,
                status: nodeOutput.error ? 'failed' : 'completed'
              };

              // Include full sheets data for inspection
              if (nodeOutput.sheets_data && Array.isArray(nodeOutput.sheets_data)) {
                fullDetails.sheets_data = nodeOutput.sheets_data;
                fullDetails.total_rows = nodeOutput.sheets_data.length;
              }

              // Include all input values for prompt checking
              if (nodeOutput.values && Array.isArray(nodeOutput.values)) {
                fullDetails.input_values = nodeOutput.values;
                fullDetails.total_inputs = nodeOutput.values.length;
              }

              // Include full processed results with prompts and content
              if (nodeOutput.processed_results && Array.isArray(nodeOutput.processed_results)) {
                fullDetails.processed_results = nodeOutput.processed_results;
                fullDetails.results_count = nodeOutput.processed_results.length;
              }

              // Include metadata (model info, processing time, etc.)
              if (nodeOutput.metadata) {
                fullDetails.metadata = nodeOutput.metadata;
              }

              // Include any error details
              if (nodeOutput.error) {
                fullDetails.error_details = nodeOutput.error;
              }

              logs.push({
                id: `detailed-${index}-${nodeId}`,
                level: nodeOutput.error ? 'error' : 'success',
                title: `${nodeId} - ${nodeOutput.operation || 'Unknown Operation'}`,
                message: nodeOutput.error ? `Failed: ${nodeOutput.error}` : `Completed successfully`,
                timestamp: event.timestamp,
                nodeId,
                executionTime: nodeOutput.execution_time_ms,
                details: fullDetails
              });
            });
          }
        }
      }
    });

    // Process standard execution logs
    safeExecutionLogs.forEach((log: ExecutionLog, index: number) => {
      const level: 'info' | 'success' | 'warning' | 'error' = 
        log.status === 'completed' ? 'success' :
        log.status === 'failed' ? 'error' :
        log.status === 'running' ? 'info' : 'warning';

      logs.push({
        id: log.id || `step-${index}`,
        level,
        title: log.step_name || 'Workflow Step',
        message: log.error_message || `Step ${log.status}`,
        timestamp: log.created_at,
        nodeId: log.step_name,
        executionTime: log.execution_time_ms,
        details: {
          step_type: log.step_name,
          status: log.status,
          error_message: log.error_message
        }
      });
    });

    // Add workflow status logs based on execution status
    if (finalStatus) {
      if (finalStatus.status === 'completed') {
        logs.unshift({
          id: 'workflow-completed',
          level: 'success',
          title: 'Workflow Completed Successfully',
          message: 'All workflow steps have been executed successfully',
          timestamp: finalStatus.completed_at || finalStatus.started_at || new Date().toISOString(),
          details: {
            instance_id: finalStatus.instance_id,
            started_at: finalStatus.started_at,
            completed_at: finalStatus.completed_at,
            is_running: finalStatus.is_running
          }
        });
      } else if (finalStatus.status === 'running') {
        logs.unshift({
          id: 'workflow-running',
          level: 'info',
          title: 'Workflow In Progress',
          message: 'Workflow is currently executing...',
          timestamp: finalStatus.started_at || new Date().toISOString(),
          details: {
            instance_id: finalStatus.instance_id,
            started_at: finalStatus.started_at,
            is_running: finalStatus.is_running
          }
        });
      }
    }

    return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [finalLogs, finalEvents, finalStatus]);

  // Storage management component
  const StorageManager: React.FC = () => {
    const [stats, setStats] = useState<any>(null);
    const [recentExecutions, setRecentExecutions] = useState<any[]>([]);

    const refreshData = () => {
      setStats(getStorageStats());
      setRecentExecutions(getRecentExecutions(10));
    };

    useEffect(() => {
      refreshData();
    }, []);

    const handleClearAll = () => {
      if (window.confirm('Are you sure you want to clear all stored execution data?')) {
        clearAllExecutions();
        refreshData();
      }
    };

    const handleExportAll = () => {
      const data = exportAllExecutions();
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `all_executions_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    };

    return (
      <div className={`absolute top-full left-0 right-0 z-50 border shadow-lg rounded-lg p-4 ${isDark ? 'bg-gray-800 border-gray-600' : 'bg-white border-gray-200'}`}>
        <div className="flex justify-between items-center mb-4">
          <h3 className={`font-semibold ${isDark ? 'text-gray-100' : 'text-gray-900'}`}>
            Storage Manager
          </h3>
          <button
            onClick={() => setShowStorageManager(false)}
            className={`text-sm ${isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700'}`}
          >
            ✕
          </button>
        </div>

        {stats && (
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className={`p-3 rounded ${isDark ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <div className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Total Instances</div>
              <div className={`text-lg ${isDark ? 'text-gray-100' : 'text-gray-900'}`}>{stats.totalInstances}</div>
            </div>
            <div className={`p-3 rounded ${isDark ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <div className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Storage Size</div>
              <div className={`text-lg ${isDark ? 'text-gray-100' : 'text-gray-900'}`}>{Math.round(stats.totalSize / 1024)} KB</div>
            </div>
          </div>
        )}

        <div className="space-y-2 mb-4">
          <h4 className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Recent Executions:</h4>
          <div className="max-h-32 overflow-y-auto">
            {recentExecutions.map((exec) => (
              <div key={exec.instanceId} className={`text-xs p-2 rounded ${isDark ? 'bg-gray-700' : 'bg-gray-50'}`}>
                <div className={`font-mono ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>{exec.instanceId.slice(0, 8)}</div>
                <div className={isDark ? 'text-gray-400' : 'text-gray-600'}>{new Date(exec.lastUpdated).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleExportAll}
            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Export All
          </button>
          <button
            onClick={handleClearAll}
            className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
          >
            Clear All
          </button>
          <button
            onClick={refreshData}
            className="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Refresh
          </button>
        </div>
      </div>
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'text-blue-600 bg-blue-100 border-blue-200';
      case 'completed':
        return 'text-green-600 bg-green-100 border-green-200';
      case 'failed':
        return 'text-red-600 bg-red-100 border-red-200';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'success':
        return 'text-green-600 bg-green-100 border-green-200';
      case 'error':
        return 'text-red-600 bg-red-100 border-red-200';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'info':
        return 'text-blue-600 bg-blue-100 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (isLoading) {
    return (
      <div className={`w-96 border-l flex items-center justify-center ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
          <div className={isDark ? 'text-gray-400' : 'text-gray-600'}>Loading execution data...</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`w-96 border-l flex flex-col relative ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
      {/* Header */}
      <div className={`p-4 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="flex items-center justify-between">
          <h3 className={`font-semibold ${isDark ? 'text-gray-100' : 'text-gray-900'}`}>
            Execution Monitor
          </h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowEmailReport(!showEmailReport)}
              className={`p-1 rounded text-xs ${isDark ? 'text-gray-400 hover:text-gray-200 bg-gray-700' : 'text-gray-500 hover:text-gray-700 bg-gray-100'}`}
              title="Send Email Report"
            >
              📧
            </button>
            <button
              onClick={() => setShowStorageManager(!showStorageManager)}
              className={`p-1 rounded text-xs ${isDark ? 'text-gray-400 hover:text-gray-200 bg-gray-700' : 'text-gray-500 hover:text-gray-700 bg-gray-100'}`}
              title="Storage Manager"
            >
              💾
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className={`p-1 rounded ${isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700'}`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        </div>
        
        {/* Execution Status */}
        {finalStatus && (
          <div className="mt-3">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(finalStatus.status)}`}>
                {finalStatus.status.toUpperCase()}
              </span>
              {finalStatus.is_running && (
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className={`text-xs ${isDark ? 'text-blue-400' : 'text-blue-600'}`}>Running</span>
                </div>
              )}
            </div>
            
            <div className={`mt-2 text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              {finalStatus.started_at && (
                <div>Started: {formatTimestamp(finalStatus.started_at)}</div>
              )}
              {finalStatus.completed_at && (
                <div>Completed: {formatTimestamp(finalStatus.completed_at)}</div>
              )}
              {finalStatus.error_message && (
                <div className="text-red-500 mt-1">Error: {finalStatus.error_message}</div>
              )}
            </div>

            {/* Email Report Button - Show for completed/failed workflows */}
            {(finalStatus.status === 'completed' || finalStatus.status === 'failed') && (
              <div className="mt-3">
                <button
                  onClick={() => setShowEmailReport(true)}
                  className={`w-full px-3 py-2 text-sm font-medium rounded-lg border transition-colors ${
                    isDark 
                      ? 'bg-blue-600 hover:bg-blue-700 text-white border-blue-600' 
                      : 'bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200'
                  }`}
                  title="Send comprehensive email report with analytics and logs"
                >
                  <div className="flex items-center justify-center gap-2">
                    <span>📧</span>
                    <span>Send Email Report</span>
                  </div>
                </button>
              </div>
            )}
          </div>
        )}

        {/* Storage indicator */}
        <div className={`mt-2 text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
          {instanceId && (
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Auto-saved to localStorage</span>
            </div>
          )}
          {error && (
            <div className="text-red-500 mt-1">{error}</div>
          )}
        </div>
      </div>

      {/* Storage Manager */}
      {showStorageManager && <StorageManager />}

      {/* Recent Executions when no current instance */}
      {!instanceId && !showStorageManager && (
        <div className={`p-4 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <h4 className={`text-sm font-medium mb-3 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
            Recent Executions
          </h4>
          <div className="space-y-2">
            {getRecentExecutions(3).map((exec) => (
              <div 
                key={exec.instanceId}
                className={`p-2 rounded cursor-pointer transition-colors ${
                  isDark 
                    ? 'bg-gray-700 hover:bg-gray-600' 
                    : 'bg-gray-50 hover:bg-gray-100'
                }`}
                onClick={() => {
                  // TODO: Load this execution
                  console.log('Load execution:', exec.instanceId);
                }}
              >
                <div className="flex justify-between items-center">
                  <div className={`font-mono text-xs ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                    {exec.instanceId.slice(0, 8)}...
                  </div>
                  <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    {new Date(exec.lastUpdated).toLocaleString()}
                  </div>
                </div>
                <div className={`text-xs mt-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  {exec.workflowName || 'Unnamed Workflow'}
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-1 py-0.5 rounded text-xs ${getStatusColor(exec.executionStatus?.status || 'unknown')}`}>
                    {exec.executionStatus?.status || 'unknown'}
                  </span>
                  <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                    {exec.executionLogs.length} logs, {exec.executionEvents.length} events
                  </span>
                </div>
              </div>
            ))}
            {getRecentExecutions().length === 0 && (
              <div className={`text-center py-8 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                <div className="text-2xl mb-2">📋</div>
                <div>No executions yet</div>
                <div className="text-xs mt-1">Execute a workflow to see results here</div>
              </div>
            )}
          </div>
        </div>
      )}

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
                  ? 'text-gray-400 hover:text-gray-200 border-transparent'
                  : 'text-gray-600 hover:text-gray-800 border-transparent'
            }`}
          >
            Events ({processedEvents.length})
          </button>
          <button 
            onClick={() => setActiveTab('logs')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'logs'
                ? isDark 
                  ? 'text-blue-400 border-blue-400 bg-gray-700' 
                  : 'text-blue-600 border-blue-600 bg-gray-50'
                : isDark
                  ? 'text-gray-400 hover:text-gray-200 border-transparent'
                  : 'text-gray-600 hover:text-gray-800 border-transparent'
            }`}
          >
            Logs ({processedLogs.length})
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {/* Events Tab */}
        {activeTab === 'events' && (
          <div className="p-4 space-y-3">
            {processedEvents.length === 0 ? (
              <div className={`text-center py-8 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p>No execution events yet</p>
                <p className="text-xs mt-1">Execute the workflow to see real-time execution steps</p>
              </div>
            ) : (
              processedEvents.map((event) => (
                <div
                  key={event.id}
                  className={`p-4 rounded-lg border ${
                    isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">⚙️</span>
                      <span className={`text-sm font-medium ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                        {event.title}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(event.status)}`}>
                        {event.status.toUpperCase()}
                      </span>
                      <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        {formatTimestamp(event.timestamp)}
                      </span>
                    </div>
                  </div>
                  
                  {/* Node ID and execution time */}
                  {(event.nodeId || event.executionTime) && (
                    <div className={`text-xs mb-2 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      {event.nodeId && <span>Node: {event.nodeId}</span>}
                      {event.executionTime && (
                        <span className="ml-3">⏱️ {event.executionTime}ms</span>
                      )}
                    </div>
                  )}
                  
                  {/* Render structured content */}
                  {event.content && Object.keys(event.content).length > 0 && (
                    <div className={`mt-3 text-xs space-y-2 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                      {Object.entries(event.content).map(([key, value]) => (
                        <div key={key}>
                          <span className={`font-medium capitalize ${isDark ? 'text-gray-200' : 'text-gray-700'}`}>{key.replace(/_/g, ' ')}: </span>
                          <span className={isDark ? 'text-gray-400' : 'text-gray-600'}>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div className="p-4 space-y-3">
            {processedLogs.length === 0 ? (
              <div className={`text-center py-8 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                <p>No logs available</p>
                <p className="text-xs mt-1">Logs will appear here as the workflow executes</p>
              </div>
            ) : (
              processedLogs.map((log) => (
                <div
                  key={log.id}
                  className={`p-3 rounded-lg border ${
                    isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium border ${getLogLevelColor(log.level)}`}>
                        {log.level.toUpperCase()}
                      </span>
                      <span className={`text-sm font-medium ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                        {log.title}
                      </span>
                    </div>
                    <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      {formatTimestamp(log.timestamp)}
                    </span>
                  </div>
                  
                  <div className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                    {log.message}
                  </div>
                  
                  {/* Execution time and node info */}
                  {(log.executionTime || log.nodeId) && (
                    <div className={`text-xs mt-2 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      {log.nodeId && <span>Node: {log.nodeId}</span>}
                      {log.executionTime && (
                        <span className={log.nodeId ? 'ml-3' : ''}>
                          ⏱️ {log.executionTime}ms
                        </span>
                      )}
                    </div>
                  )}
                  
                  {/* Additional details */}
                  {log.details && Object.keys(log.details).length > 0 && (
                    <details className="mt-3">
                      <summary className={`cursor-pointer text-xs font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>View Details</summary>
                      <div className="mt-2 space-y-2">
                        {Object.entries(log.details).map(([key, value]) => (
                          <div key={key} className="text-xs">
                            <span className={`font-medium capitalize ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>{key.replace(/_/g, ' ')}: </span>
                            <span className={`break-words ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                              {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className={`p-3 border-t text-xs ${
        isDark ? 'border-gray-700 text-gray-400' : 'border-gray-200 text-gray-500'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className={isDark ? 'text-gray-300' : 'text-gray-700'}>Real-time updates</span>
            </div>
            <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              💾 Persistent storage enabled
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Export Button */}
            {instanceId && (
              <button
                onClick={() => {
                  const data = exportExecution(instanceId);
                  if (data) {
                    const blob = new Blob([data], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `execution_${instanceId.substring(0, 8)}_${new Date().toISOString().split('T')[0]}.json`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                  }
                }}
                className={`px-2 py-1 rounded text-xs border transition-colors ${
                  isDark 
                    ? 'bg-gray-600 border-gray-500 text-gray-300 hover:bg-gray-500' 
                    : 'bg-gray-100 border-gray-300 text-gray-600 hover:bg-gray-200'
                }`}
                title="Export execution data to JSON file"
              >
                📥 Export
              </button>
            )}
            {/* Email Report Button */}
            {instanceId && (
              <button
                onClick={() => setShowEmailReport(true)}
                className={`px-2 py-1 rounded text-xs border transition-colors ${
                  isDark 
                    ? 'bg-blue-600 border-blue-500 text-blue-100 hover:bg-blue-500' 
                    : 'bg-blue-100 border-blue-300 text-blue-600 hover:bg-blue-200'
                }`}
                title="Send comprehensive email report"
              >
                📧 Email Report
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Email Report Modal */}
      {showEmailReport && (
        <EmailReportPanel
          instanceId={instanceId}
          workflowName={workflowName}
          executionStatus={finalStatus}
          onClose={() => setShowEmailReport(false)}
        />
      )}
    </div>
  );
};

export default EnhancedExecutionPanel;
