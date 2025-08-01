/**
 * Workflow Runner - Real-time workflow execution monitoring
 */
import React, { useState, useEffect } from 'react';
import { useWorkflowInstance } from '../../hooks/useWorkflow';
// import { WorkflowInstance } from '../../services/workflowApi';

interface WorkflowRunnerProps {
  instanceId: string;
  onClose?: () => void;
}

export const WorkflowRunner: React.FC<WorkflowRunnerProps> = ({ 
  instanceId, 
  onClose 
}) => {
  const { instance, loading, error, refetch } = useWorkflowInstance(instanceId);
  const [logs, setLogs] = useState<string[]>([]);

  // Add mock logs for demonstration
  useEffect(() => {
    if (instance?.status === 'running') {
      const interval = setInterval(() => {
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Processing step...`]);
      }, 2000);
      
      return () => clearInterval(interval);
    }
  }, [instance?.status]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'text-blue-600 bg-blue-100';
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
        );
      case 'completed':
        return (
          <svg className="h-4 w-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'failed':
        return (
          <svg className="h-4 w-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <div className="h-4 w-4 rounded-full bg-gray-400"></div>
        );
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
          <p className="text-center mt-4 text-gray-600 dark:text-gray-400">
            Loading workflow instance...
          </p>
        </div>
      </div>
    );
  }

  if (error || !instance) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
          <div className="text-center">
            <svg className="h-12 w-12 text-red-600 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Error Loading Workflow
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {error || 'Workflow instance not found'}
            </p>
            <button
              onClick={onClose}
              className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gray-50 dark:bg-gray-700 px-6 py-4 border-b border-gray-200 dark:border-gray-600">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                {instance.name}
              </h2>
              <div className="flex items-center mt-1">
                {getStatusIcon(instance.status)}
                <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(instance.status)}`}>
                  {instance.status.toUpperCase()}
                </span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Workflow Information */}
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                  Workflow Information
                </h3>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Created:</span>
                    <span className="text-gray-900 dark:text-white">
                      {new Date(instance.created_at).toLocaleString()}
                    </span>
                  </div>
                  {instance.started_at && (
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Started:</span>
                      <span className="text-gray-900 dark:text-white">
                        {new Date(instance.started_at).toLocaleString()}
                      </span>
                    </div>
                  )}
                  {instance.completed_at && (
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Completed:</span>
                      <span className="text-gray-900 dark:text-white">
                        {new Date(instance.completed_at).toLocaleString()}
                      </span>
                    </div>
                  )}
                  {instance.started_at && instance.completed_at && (
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Duration:</span>
                      <span className="text-gray-900 dark:text-white">
                        {Math.round((new Date(instance.completed_at).getTime() - new Date(instance.started_at).getTime()) / 1000)}s
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Input Data */}
              {instance.input_data && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                    Input Data
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <pre className="text-sm text-gray-800 dark:text-gray-200 overflow-x-auto">
                      {JSON.stringify(instance.input_data, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Output Data */}
              {instance.output_data && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                    Output Data
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <pre className="text-sm text-gray-800 dark:text-gray-200 overflow-x-auto">
                      {JSON.stringify(instance.output_data, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Error Message */}
              {instance.error_message && (
                <div>
                  <h3 className="text-lg font-medium text-red-600 dark:text-red-400 mb-3">
                    Error Details
                  </h3>
                  <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4">
                    <p className="text-sm text-red-800 dark:text-red-200">
                      {instance.error_message}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Execution Logs */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                Execution Logs
              </h3>
              <div className="bg-black rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm">
                <div className="text-green-400">
                  {instance.status === 'running' && (
                    <div className="text-blue-400 mb-2">
                      🔄 Workflow is currently running...
                    </div>
                  )}
                  {instance.status === 'completed' && (
                    <div className="text-green-400 mb-2">
                      ✅ Workflow completed successfully!
                    </div>
                  )}
                  {instance.status === 'failed' && (
                    <div className="text-red-400 mb-2">
                      ❌ Workflow execution failed
                    </div>
                  )}
                  
                  <div className="text-gray-400 mb-2">
                    [{new Date(instance.created_at).toLocaleTimeString()}] Workflow instance created
                  </div>
                  
                  {instance.started_at && (
                    <div className="text-blue-400 mb-2">
                      [{new Date(instance.started_at).toLocaleTimeString()}] Workflow execution started
                    </div>
                  )}
                  
                  {logs.map((log, index) => (
                    <div key={index} className="text-white mb-1">
                      {log}
                    </div>
                  ))}
                  
                  {instance.completed_at && (
                    <div className="text-green-400 mb-2">
                      [{new Date(instance.completed_at).toLocaleTimeString()}] Workflow execution completed
                    </div>
                  )}
                  
                  {instance.status === 'running' && (
                    <div className="text-white">
                      <span className="animate-pulse">▋</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 dark:bg-gray-700 px-6 py-4 border-t border-gray-200 dark:border-gray-600">
          <div className="flex justify-between items-center">
            <button
              onClick={refetch}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
            >
              Refresh
            </button>
            <button
              onClick={onClose}
              className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowRunner;
