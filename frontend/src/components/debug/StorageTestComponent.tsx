/**
 * Debug component to test localStorage functionality
 */
import React, { useState, useEffect } from 'react';
import { useExecutionStorage } from '../../hooks/useExecutionStorage';
import { debugLocalStorage, clearDebugStorage } from '../../utils/debugStorage';

const StorageTestComponent: React.FC = () => {
  const [testInstanceId, setTestInstanceId] = useState('test-instance-123');
  const {
    executionStatus,
    executionLogs, 
    executionEvents,
    saveExecution,
    loadExecution,
    // getAllExecutions, // Commented out as it's not used
    getStorageStats
  } = useExecutionStorage(testInstanceId);

  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    setStats(getStorageStats());
  }, [getStorageStats]);

  const handleSaveTestData = () => {
    const testStatus = {
      id: testInstanceId,
      instance_id: testInstanceId,
      status: 'completed' as const,
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      is_running: false,
      error_message: undefined
    };

    const testLogs = [
      {
        id: '1',
        step_name: 'Test Step 1',
        status: 'completed',
        created_at: new Date().toISOString(),
        execution_time_ms: 100
      },
      {
        id: '2', 
        step_name: 'Test Step 2',
        status: 'completed',
        created_at: new Date().toISOString(),
        execution_time_ms: 200
      }
    ];

    const testEvents = [
      {
        id: '1',
        event_type: 'execution_started',
        timestamp: new Date().toISOString(),
        data: { message: 'Test event 1' }
      },
      {
        id: '2',
        event_type: 'execution_completed', 
        timestamp: new Date().toISOString(),
        data: { message: 'Test event 2' }
      }
    ];

    const success = saveExecution(testInstanceId, testStatus, testLogs, testEvents, 'Test Workflow');
    console.log('Save result:', success);
    
    // Update stats
    setStats(getStorageStats());
  };

  const handleLoadTestData = () => {
    const loaded = loadExecution(testInstanceId);
    console.log('Loaded data:', loaded);
  };

  const handleDebugStorage = () => {
    debugLocalStorage();
  };

  const handleClearStorage = () => {
    clearDebugStorage();
    setStats(getStorageStats());
  };

  return (
    <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
      <h3 className="text-lg font-bold mb-4">🧪 Storage Test Component</h3>
      
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Test Instance ID:</label>
        <input 
          type="text"
          value={testInstanceId}
          onChange={(e) => setTestInstanceId(e.target.value)}
          className="w-full p-2 border rounded"
        />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <button 
          onClick={handleSaveTestData}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          💾 Save Test Data
        </button>
        
        <button 
          onClick={handleLoadTestData}
          className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
        >
          📂 Load Test Data
        </button>

        <button 
          onClick={handleDebugStorage}
          className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
        >
          🔍 Debug Storage
        </button>

        <button 
          onClick={handleClearStorage}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          🧹 Clear All
        </button>
      </div>

      <div className="bg-white dark:bg-gray-700 p-4 rounded">
        <h4 className="font-bold mb-2">Current Hook State:</h4>
        <div className="text-sm space-y-1">
          <div>Status: {executionStatus ? executionStatus.status : 'None'}</div>
          <div>Logs: {executionLogs.length}</div>
          <div>Events: {executionEvents.length}</div>
        </div>
      </div>

      {stats && (
        <div className="bg-white dark:bg-gray-700 p-4 rounded mt-4">
          <h4 className="font-bold mb-2">Storage Stats:</h4>
          <div className="text-sm space-y-1">
            <div>Total Instances: {stats.totalInstances}</div>
            <div>Total Size: {Math.round(stats.totalSize / 1024)} KB</div>
            <div>Oldest Entry: {stats.oldestEntry ? new Date(stats.oldestEntry).toLocaleString() : 'None'}</div>
            <div>Newest Entry: {stats.newestEntry ? new Date(stats.newestEntry).toLocaleString() : 'None'}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StorageTestComponent;
