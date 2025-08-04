/**
 * Debug Page for Storage Testing
 */
import React from 'react';
import StorageTestComponent from '../components/debug/StorageTestComponent';
import EnhancedExecutionPanel from '../components/WorkflowEditor/EnhancedExecutionPanel';

const StorageDebugPage: React.FC = () => {
  // Test data for ExecutionPanel
  const testStatus = {
    id: 'debug-test-123',
    instance_id: 'debug-test-123',
    status: 'completed' as const,
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    is_running: false
  };

  const testLogs = [
    {
      id: '1',
      step_name: 'Initialize Process',
      status: 'completed',
      created_at: new Date().toISOString(),
      execution_time_ms: 150
    },
    {
      id: '2',
      step_name: 'Process Data',
      status: 'completed', 
      created_at: new Date().toISOString(),
      execution_time_ms: 300
    }
  ];

  const testEvents = [
    {
      id: '1',
      event_type: 'execution_started',
      timestamp: new Date().toISOString(),
      data: { message: 'Execution started' }
    },
    {
      id: '2',
      event_type: 'execution_completed',
      timestamp: new Date().toISOString(),
      data: { message: 'Execution completed successfully' }
    }
  ];

  return (
    <div className="p-8 space-y-8 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100">
        🧪 Storage Debug Page
      </h1>
      
      <div className="bg-yellow-100 dark:bg-yellow-900 p-4 rounded-lg">
        <h2 className="text-lg font-bold text-yellow-800 dark:text-yellow-200 mb-2">
          ⚠️ Instructions
        </h2>
        <ol className="list-decimal list-inside text-yellow-800 dark:text-yellow-200 space-y-1">
          <li>Open Browser DevTools (F12)</li>
          <li>Go to Console tab to see debug logs</li>
          <li>Use Storage Test Component to save test data</li>
          <li>Reload page to test persistence</li>
          <li>Check Application &gt; Local Storage in DevTools</li>
        </ol>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Storage Test Component */}
        <div>
          <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-gray-100">
            Storage Test Controls
          </h2>
          <StorageTestComponent />
        </div>

        {/* Enhanced Execution Panel */}
        <div>
          <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-gray-100">
            Enhanced Execution Panel
          </h2>
          <EnhancedExecutionPanel
            executionStatus={testStatus}
            executionLogs={testLogs}
            executionEvents={testEvents}
            instanceId="debug-test-123"
            workflowName="Debug Test Workflow"
          />
        </div>
      </div>

      <div className="bg-blue-100 dark:bg-blue-900 p-4 rounded-lg">
        <h2 className="text-lg font-bold text-blue-800 dark:text-blue-200 mb-2">
          🔍 Debug Commands (Console)
        </h2>
        <div className="text-blue-800 dark:text-blue-200 space-y-1 font-mono text-sm">
          <div>debugStorage() - Show all localStorage data</div>
          <div>clearStorage() - Clear all execution data</div>
        </div>
      </div>
    </div>
  );
};

export default StorageDebugPage;
