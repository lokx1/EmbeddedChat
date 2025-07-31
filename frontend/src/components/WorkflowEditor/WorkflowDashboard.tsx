/**
 * Workflow Dashboard - Main interface for workflow management
 * Integrates with backend API for full workflow automation
 */
import React, { useState, useEffect } from 'react';
import { 
  useWorkflowInstances, 
  useWorkflowTemplates,
  useTaskLogs,
  useAnalytics,
  useBackendHealth,
  useGoogleSheets
} from '../../hooks/useWorkflow';
import { WorkflowInstance, WorkflowTemplate } from '../../services/workflowApi';

interface WorkflowDashboardProps {
  onOpenEditor?: () => void;
}

export const WorkflowDashboard: React.FC<WorkflowDashboardProps> = ({ onOpenEditor }) => {
  const [activeTab, setActiveTab] = useState<'instances' | 'templates' | 'logs' | 'analytics' | 'sheets'>('instances');
  const [selectedInstance, setSelectedInstance] = useState<WorkflowInstance | null>(null);

  // Backend integration hooks
  const { isHealthy, checkHealth } = useBackendHealth();
  const { 
    instances, 
    loading: instancesLoading, 
    error: instancesError,
    fetchInstances,
    createInstance,
    executeInstance 
  } = useWorkflowInstances();
  
  const {
    templates,
    loading: templatesLoading,
    error: templatesError,
    fetchTemplates,
    createTemplate
  } = useWorkflowTemplates();

  const {
    logs,
    loading: logsLoading,
    error: logsError,
    fetchLogs
  } = useTaskLogs();

  const {
    dailyData,
    weeklyData,
    loading: analyticsLoading,
    error: analyticsError,
    fetchDailyAnalytics,
    fetchWeeklyAnalytics,
    generateDailyReport
  } = useAnalytics();

  const {
    loading: sheetsLoading,
    error: sheetsError,
    processSheets
  } = useGoogleSheets();

  // Load initial data
  useEffect(() => {
    fetchInstances();
    fetchTemplates();
    fetchLogs({ limit: 50 });
    
    // Fetch today's analytics
    const today = new Date().toISOString().split('T')[0];
    fetchDailyAnalytics(today);
  }, [fetchInstances, fetchTemplates, fetchLogs, fetchDailyAnalytics]);

  // Handle workflow execution
  const handleExecuteWorkflow = async (instanceId: string) => {
    const result = await executeInstance(instanceId);
    if (result.success) {
      alert(`Workflow execution started for instance: ${instanceId}`);
    } else {
      alert(`Failed to execute workflow: ${result.error}`);
    }
  };

  // Handle Google Sheets processing
  const handleProcessSheets = async (sheetsId: string) => {
    const result = await processSheets({
      google_sheets_id: sheetsId,
      notification_settings: {
        email: 'admin@company.com',
        slack_channel: '#workflow-notifications'
      },
      output_settings: {
        format: 'pdf',
        drive_folder: 'workflow_outputs'
      }
    });
    
    if (result.success) {
      alert(`Google Sheets processing started for: ${sheetsId}`);
    } else {
      alert(`Failed to process sheets: ${result.error}`);
    }
  };

  // Handle daily report generation
  const handleGenerateReport = async () => {
    const result = await generateDailyReport();
    if (result.success) {
      alert('Daily report generation started');
    } else {
      alert(`Failed to generate report: ${result.error}`);
    }
  };

  // Create new workflow instance
  const handleCreateInstance = async () => {
    const workflowData = {
      nodes: [
        { id: '1', type: 'input', position: { x: 100, y: 100 }, data: { label: 'Google Sheets Input', type: 'sheets' } },
        { id: '2', type: 'ai', position: { x: 300, y: 100 }, data: { label: 'AI Processing', type: 'openai' } },
        { id: '3', type: 'output', position: { x: 500, y: 100 }, data: { label: 'Google Drive Output', type: 'drive' } }
      ],
      edges: [
        { id: 'e1-2', source: '1', target: '2' },
        { id: 'e2-3', source: '2', target: '3' }
      ]
    };

    const result = await createInstance({
      name: `Workflow Instance ${Date.now()}`,
      workflow_data: workflowData,
      input_data: {
        sheets_id: 'example-sheets-id',
        ai_prompt: 'Generate product descriptions',
        output_format: 'pdf'
      }
    });

    if (result.success) {
      alert('Workflow instance created successfully');
    } else {
      alert(`Failed to create instance: ${result.error}`);
    }
  };

  if (!isHealthy) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Backend Unavailable</h3>
              <p className="text-sm text-red-700 mt-1">
                Cannot connect to the backend service. Please ensure the backend is running on http://localhost:8000
              </p>
              <button 
                onClick={checkHealth}
                className="mt-2 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
              >
                Retry Connection
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Workflow Automation Dashboard
              </h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Manage and monitor your automated workflows
              </p>
            </div>
            {onOpenEditor && (
              <button
                onClick={onOpenEditor}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create New Workflow
              </button>
            )}
          </div>
        </div>

        {/* Health Status */}
        <div className="mb-6">
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            isHealthy 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-2 ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`} />
            Backend {isHealthy ? 'Connected' : 'Disconnected'}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'instances', label: 'Workflow Instances', count: instances.length },
              { id: 'templates', label: 'Templates', count: templates.length },
              { id: 'logs', label: 'Task Logs', count: logs.length },
              { id: 'analytics', label: 'Analytics' },
              { id: 'sheets', label: 'Google Sheets' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                {tab.label}
                {tab.count !== undefined && (
                  <span className="ml-2 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 py-0.5 px-2 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'instances' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Workflow Instances
              </h2>
              <button
                onClick={handleCreateInstance}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create New Instance
              </button>
            </div>

            {instancesLoading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : instancesError ? (
              <div className="text-red-600 dark:text-red-400 py-4">
                Error: {instancesError}
              </div>
            ) : (
              <div className="grid gap-4">
                {instances.map((instance) => (
                  <div
                    key={instance.id}
                    className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                          {instance.name}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          Created: {new Date(instance.created_at).toLocaleDateString()}
                        </p>
                        <div className="mt-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            instance.status === 'completed' 
                              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                              : instance.status === 'running'
                              ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                              : instance.status === 'failed'
                              ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                              : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                          }`}>
                            {instance.status.toUpperCase()}
                          </span>
                        </div>
                        {instance.error_message && (
                          <p className="text-sm text-red-600 dark:text-red-400 mt-2">
                            Error: {instance.error_message}
                          </p>
                        )}
                      </div>
                      <div className="flex space-x-2">
                        {instance.status === 'draft' && (
                          <button
                            onClick={() => handleExecuteWorkflow(instance.id)}
                            className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 text-sm transition-colors"
                          >
                            Execute
                          </button>
                        )}
                        <button
                          onClick={() => setSelectedInstance(instance)}
                          className="bg-gray-600 text-white px-3 py-1 rounded hover:bg-gray-700 text-sm transition-colors"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'sheets' && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Google Sheets Processing
            </h2>
            
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Process Google Sheets
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Google Sheets ID
                  </label>
                  <input
                    type="text"
                    placeholder="Enter Google Sheets ID"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    id="sheets-id-input"
                  />
                </div>
                
                <button
                  onClick={() => {
                    const input = document.getElementById('sheets-id-input') as HTMLInputElement;
                    if (input?.value) {
                      handleProcessSheets(input.value);
                    }
                  }}
                  disabled={sheetsLoading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {sheetsLoading ? 'Processing...' : 'Process Sheets'}
                </button>
                
                {sheetsError && (
                  <p className="text-red-600 dark:text-red-400 text-sm">
                    Error: {sheetsError}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Analytics & Reports
              </h2>
              <button
                onClick={handleGenerateReport}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
              >
                Generate Daily Report
              </button>
            </div>

            {analyticsLoading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : analyticsError ? (
              <div className="text-red-600 dark:text-red-400 py-4">
                Error: {analyticsError}
              </div>
            ) : dailyData ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                  <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Tasks</h3>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                    {dailyData.total_tasks || 0}
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                  <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Successful</h3>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-2">
                    {dailyData.successful_tasks || 0}
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                  <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Failed</h3>
                  <p className="text-2xl font-bold text-red-600 dark:text-red-400 mt-2">
                    {dailyData.failed_tasks || 0}
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                  <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Success Rate</h3>
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-2">
                    {dailyData.success_rate?.toFixed(1) || 0}%
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-600 dark:text-gray-400">
                No analytics data available
              </div>
            )}
          </div>
        )}

        {/* Additional tabs content... */}
      </div>
    </div>
  );
};

export default WorkflowDashboard;
