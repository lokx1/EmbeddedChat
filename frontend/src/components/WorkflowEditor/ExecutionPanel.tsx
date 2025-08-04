/**
 * Execution Panel for Real-time Workflow Monitoring
 */
import React, { useState, useMemo, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { ExecutionStatus, ExecutionLog, ExecutionEvent } from '../../services/enhancedWorkflowEditorApi';

interface ExecutionPanelProps {
  executionStatus: ExecutionStatus | null;
  executionLogs: ExecutionLog[];
  executionEvents: ExecutionEvent[];
  instanceId?: string;
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

const ExecutionPanel: React.FC<ExecutionPanelProps> = ({
  executionStatus,
  executionLogs = [],
  executionEvents = [],
  instanceId,
  onClose
}) => {
  const { isDark } = useTheme() || { isDark: false };
  const [activeTab, setActiveTab] = useState<'events' | 'logs'>('events');

  // Storage functionality
  const STORAGE_KEY_PREFIX = 'workflow_execution_';
  const getStorageKey = (id: string, type: string) => `${STORAGE_KEY_PREFIX}${id}_${type}`;

  // Auto-save execution data when it changes
  useEffect(() => {
    if (instanceId && (executionStatus || executionLogs.length > 0 || executionEvents.length > 0)) {
      try {
        if (executionStatus) {
          localStorage.setItem(getStorageKey(instanceId, 'status'), JSON.stringify(executionStatus));
        }
        if (executionLogs.length > 0) {
          localStorage.setItem(getStorageKey(instanceId, 'logs'), JSON.stringify(executionLogs));
        }
        if (executionEvents.length > 0) {
          localStorage.setItem(getStorageKey(instanceId, 'events'), JSON.stringify(executionEvents));
        }
        localStorage.setItem(getStorageKey(instanceId, 'updated'), new Date().toISOString());
        console.log('💾 Auto-saved execution data for:', instanceId);
      } catch (error) {
        console.warn('Failed to save execution data:', error);
      }
    }
  }, [instanceId, executionStatus, executionLogs, executionEvents]);

  // Load saved data if current data is empty
  const loadSavedData = (id: string) => {
    try {
      const savedStatus = localStorage.getItem(getStorageKey(id, 'status'));
      const savedLogs = localStorage.getItem(getStorageKey(id, 'logs'));
      const savedEvents = localStorage.getItem(getStorageKey(id, 'events'));
      
      return {
        status: savedStatus ? JSON.parse(savedStatus) : null,
        logs: savedLogs ? JSON.parse(savedLogs) : [],
        events: savedEvents ? JSON.parse(savedEvents) : []
      };
    } catch (error) {
      console.warn('Failed to load saved data:', error);
      return { status: null, logs: [], events: [] };
    }
  };

  // Get effective data (current or saved)
  const savedData = instanceId ? loadSavedData(instanceId) : { status: null, logs: [], events: [] };
  const effectiveStatus = executionStatus || savedData.status;
  const effectiveLogs = executionLogs.length > 0 ? executionLogs : savedData.logs;
  const effectiveEvents = executionEvents.length > 0 ? executionEvents : savedData.events;

  // Safe guard against undefined arrays
  const safeExecutionLogs = effectiveLogs || [];
  const safeExecutionEvents = effectiveEvents || [];

  // Process events - Transform raw execution events into concise summary events
  const processedEvents = useMemo((): ProcessedEvent[] => {
    const events: ProcessedEvent[] = [];

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
  }, [safeExecutionEvents]);

  // Process logs - Transform execution logs into detailed logs with full content
  const processedLogs = useMemo((): ProcessedLog[] => {
    const logs: ProcessedLog[] = [];

    // Process execution events for DETAILED logs content
    safeExecutionEvents.forEach((event: ExecutionEvent, index: number) => {
      if (event.data && typeof event.data === 'object') {
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
    if (effectiveStatus) {
      if (effectiveStatus.status === 'completed') {
        logs.unshift({
          id: 'workflow-completed',
          level: 'success',
          title: 'Workflow Completed Successfully',
          message: 'All workflow steps have been executed successfully',
          timestamp: effectiveStatus.completed_at || new Date().toISOString(),
          details: {
            instance_id: effectiveStatus.instance_id,
            started_at: effectiveStatus.started_at,
            completed_at: effectiveStatus.completed_at,
            total_execution_time: effectiveStatus.started_at && effectiveStatus.completed_at 
              ? Math.round((new Date(effectiveStatus.completed_at).getTime() - new Date(effectiveStatus.started_at).getTime()) / 1000)
              : undefined
          }
        });
      } else if (effectiveStatus.status === 'failed') {
        logs.unshift({
          id: 'workflow-failed',
          level: 'error',
          title: 'Workflow Execution Failed',
          message: effectiveStatus.error_message || 'Workflow execution encountered an error',
          timestamp: effectiveStatus.completed_at || new Date().toISOString(),
          details: {
            instance_id: effectiveStatus.instance_id,
            error_message: effectiveStatus.error_message,
            started_at: effectiveStatus.started_at,
            failed_at: effectiveStatus.completed_at
          }
        });
      } else if (effectiveStatus.status === 'running') {
        logs.unshift({
          id: 'workflow-running',
          level: 'info',
          title: 'Workflow In Progress',
          message: 'Workflow is currently executing...',
          timestamp: effectiveStatus.started_at || new Date().toISOString(),
          details: {
            instance_id: effectiveStatus.instance_id,
            started_at: effectiveStatus.started_at,
            is_running: effectiveStatus.is_running
          }
        });
      }
    }

    return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [safeExecutionLogs, safeExecutionEvents, effectiveStatus]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'text-blue-600 bg-blue-100 border-blue-200';
      case 'completed':
        return 'text-green-600 bg-green-100 border-green-200';
      case 'failed':
        return 'text-red-600 bg-red-100 border-red-200';
      case 'cancelled':
        return 'text-gray-600 bg-gray-100 border-gray-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getLogLevelColor = (level: ProcessedLog['level']) => {
    switch (level) {
      case 'success':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'info':
      default:
        return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getEventTypeIcon = (type: ProcessedEvent['type']) => {
    switch (type) {
      case 'node_execution':
        return '⚙️';
      case 'workflow_step':
        return '🔄';
      case 'data_processing':
        return '📊';
      case 'system_event':
      default:
        return '📋';
    }
  };

  // Helper function to render log details with proper formatting and overflow control
  const renderLogDetail = (value: any): JSX.Element => {
    if (value === null || value === undefined) {
      return <span className="text-gray-400 italic">Not available</span>;
    }
    
    if (typeof value === 'boolean') {
      return <span className={value ? 'text-green-600' : 'text-red-600'}>{value ? 'Yes' : 'No'}</span>;
    }
    
    if (typeof value === 'number') {
      return <span className="text-blue-600 font-mono">{value.toLocaleString()}</span>;
    }
    
    if (typeof value === 'string') {
      // Handle long strings with proper wrapping and scrollable container
      if (value.length > 100) {
        return (
          <div className="space-y-2">
            <div className="text-xs bg-gray-100 rounded p-2 max-h-32 overflow-y-auto border">
              <pre className="whitespace-pre-wrap text-xs font-mono break-words text-gray-700">
                {value}
              </pre>
            </div>
            <div className="text-xs text-gray-500">
              {value.length} characters
            </div>
          </div>
        );
      }
      return <span className="break-words text-gray-700">{value}</span>;
    }
    
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return <span className="text-gray-400 italic">Empty array</span>;
      }
      
      return (
        <div className="space-y-2">
          <div className="text-xs text-gray-600 font-medium">
            Array with {value.length} items
          </div>
          <details className="group">
            <summary className="cursor-pointer text-xs text-blue-600 hover:text-blue-800 font-medium">
              View Array Contents
            </summary>
            <div className="mt-2 bg-gray-50 rounded p-2 max-h-40 overflow-y-auto border">
              <pre className="text-xs font-mono whitespace-pre-wrap break-words text-gray-700">
                {JSON.stringify(value, null, 2)}
              </pre>
            </div>
          </details>
        </div>
      );
    }
    
    if (typeof value === 'object') {
      const entries = Object.entries(value);
      if (entries.length === 0) {
        return <span className="text-gray-400 italic">Empty object</span>;
      }
      
      return (
        <div className="space-y-2">
          <div className="text-xs text-gray-600 font-medium">
            Object with {entries.length} properties
          </div>
          <details className="group">
            <summary className="cursor-pointer text-xs text-blue-600 hover:text-blue-800 font-medium">
              View Object Details
            </summary>
            <div className="mt-2 bg-gray-50 rounded p-2 max-h-40 overflow-y-auto border">
              <pre className="text-xs font-mono whitespace-pre-wrap break-words text-gray-700">
                {JSON.stringify(value, null, 2)}
              </pre>
            </div>
          </details>
        </div>
      );
    }
    
    return <span className="break-words text-gray-700">{String(value)}</span>;
  };

  // Export function for current execution data
  const exportCurrentData = () => {
    if (!instanceId) {
      alert('❌ No instance ID available for export');
      return;
    }

    const dataToExport = {
      instanceId,
      exportedAt: new Date().toISOString(),
      executionStatus: effectiveStatus,
      executionLogs: effectiveLogs,
      executionEvents: effectiveEvents,
      processedEvents,
      processedLogs,
      metadata: {
        totalEvents: processedEvents.length,
        totalLogs: processedLogs.length,
        hasRealTimeData: executionLogs.length > 0 || executionEvents.length > 0,
        dataSource: executionLogs.length > 0 ? 'realtime' : 'localStorage'
      }
    };

    const dataStr = JSON.stringify(dataToExport, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `workflow_execution_${instanceId.substring(0, 8)}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    console.log('📥 Exported execution data:', dataToExport);
    alert('✅ Execution data exported successfully!');
  };

  const renderEventContent = (event: ProcessedEvent) => {
    const { content } = event;
    
    if (!content || Object.keys(content).length === 0) {
      return null;
    }

    return (
      <div className={`mt-3 text-xs space-y-2 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
        {/* Show processed results count */}
        {content.results_count && (
          <div className="flex items-center gap-2">
            <span className="font-medium">Processed Results:</span>
            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
              {content.results_count} items
            </span>
          </div>
        )}
        
        {/* Show example input values */}
        {content.example_values && Array.isArray(content.example_values) && (
          <div>
            <span className="font-medium">Example Inputs:</span>
            <div className="mt-1 space-y-1">
              {content.example_values.map((value: any, idx: number) => (
                <div key={idx} className={`p-2 rounded text-xs font-mono ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                  {Array.isArray(value) ? value.join(', ') : String(value)}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Show operation details */}
        {content.operation && (
          <div>
            <span className="font-medium">Operation:</span>
            <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
              {content.operation}
            </span>
          </div>
        )}
        
        {/* Show processed rows */}
        {content.processed_rows && (
          <div>
            <span className="font-medium">Rows Processed:</span>
            <span className="ml-2">{content.processed_rows}</span>
          </div>
        )}
        
        {/* Fallback to JSON for complex content */}
        {Object.keys(content).some(key => !['results_count', 'example_values', 'operation', 'processed_rows'].includes(key)) && (
          <details className="mt-2">
            <summary className="cursor-pointer font-medium">View Raw Data</summary>
            <pre className="mt-1 p-2 text-xs font-mono whitespace-pre-wrap bg-gray-100 dark:bg-gray-700 rounded">
              {JSON.stringify(content, null, 2)}
            </pre>
          </details>
        )}
      </div>
    );
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
                      <span className="text-lg">{getEventTypeIcon(event.type)}</span>
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
                  {renderEventContent(event)}
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
                  
                  {/* Additional details with improved formatting */}
                  {log.details && Object.keys(log.details).length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <div className="text-xs text-gray-600 mb-2 font-medium">Detailed Information:</div>
                      <div className="space-y-3">
                        {Object.entries(log.details).map(([key, value]) => (
                          <div key={key} className="bg-gray-50 rounded-lg p-3">
                            <div className="text-xs font-medium text-gray-700 mb-2 capitalize">
                              {key.replace(/_/g, ' ')}:
                            </div>
                            <div className="ml-2">
                              {renderLogDetail(value)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
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
              <span>Real-time updates</span>
            </div>
            {savedData && savedData.status && (
              <span className="text-xs">
                💾 Data auto-saved
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {/* Export Button */}
            <button
              onClick={exportCurrentData}
              disabled={!instanceId}
              className={`px-2 py-1 rounded text-xs border transition-colors ${
                !instanceId 
                  ? 'opacity-50 cursor-not-allowed bg-gray-100 border-gray-300' 
                  : isDark 
                    ? 'bg-gray-600 border-gray-500 text-gray-300 hover:bg-gray-500' 
                    : 'bg-gray-100 border-gray-300 text-gray-600 hover:bg-gray-200'
              }`}
              title={instanceId ? 'Export execution data to JSON file' : 'No instance ID available'}
            >
              📥 Export
            </button>
            
            {/* Info */}
            <div className="flex items-center gap-1">
              <span>Connected</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExecutionPanel;
