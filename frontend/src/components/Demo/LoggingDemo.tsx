/**
 * Demo Component to showcase Enhanced Logging Integration
 */
import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { useEnhancedLogging } from '../../services/enhancedLoggingService';
import { useExecutionMonitor } from '../../hooks/useExecutionMonitor';
import EnhancedExecutionPanel from '../WorkflowEditor/EnhancedExecutionPanel';
import FloatingExecutionMonitor from '../WorkflowEditor/FloatingExecutionMonitor';

const LoggingDemo: React.FC = () => {
  const { isDark } = useTheme() || { isDark: false };
  const [demoInstanceId, setDemoInstanceId] = useState<string>('demo-instance-123');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string>('');
  
  const { getTaskLogs, getExecutionSteps, getLogSummary, healthCheck } = useEnhancedLogging();
  const executionMonitor = useExecutionMonitor();

  const runHealthCheck = async () => {
    setIsLoading(true);
    setMessage('Checking backend health...');
    
    try {
      const result = await healthCheck();
      setMessage(result.success 
        ? '✅ Backend is healthy and logging endpoints are working!' 
        : `❌ Backend health check failed: ${result.error}`
      );
    } catch (error) {
      setMessage(`❌ Health check error: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const testLoggingEndpoints = async () => {
    setIsLoading(true);
    setMessage('Testing logging endpoints...');
    
    try {
      const [summaryResult, tasksResult, stepsResult] = await Promise.all([
        getLogSummary(),
        getTaskLogs({ limit: 5 }),
        getExecutionSteps({ limit: 5 })
      ]);

      const results = [];
      if (summaryResult.success) {
        results.push(`✅ Summary: ${summaryResult.data?.total_task_logs} task logs, ${summaryResult.data?.total_execution_steps} steps`);
      } else {
        results.push(`❌ Summary failed: ${summaryResult.error}`);
      }

      if (tasksResult.success) {
        results.push(`✅ Task logs: ${tasksResult.data?.length || 0} entries found`);
      } else {
        results.push(`❌ Task logs failed: ${tasksResult.error}`);
      }

      if (stepsResult.success) {
        results.push(`✅ Execution steps: ${stepsResult.data?.length || 0} entries found`);
      } else {
        results.push(`❌ Execution steps failed: ${stepsResult.error}`);
      }

      setMessage(results.join('\n'));
    } catch (error) {
      setMessage(`❌ Endpoint test error: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const showExecutionMonitor = () => {
    executionMonitor.setWorkflowInstance(demoInstanceId);
    executionMonitor.showPanel(demoInstanceId);
    setMessage('📊 Execution monitor opened! Check the right panel.');
  };

  const createDemoWorkflow = async () => {
    setIsLoading(true);
    setMessage('Creating demo workflow instance...');
    
    try {
      // Create a demo workflow instance for testing
      const instanceData = {
        name: `Demo Logging Test - ${new Date().toLocaleTimeString()}`,
        workflow_data: {
          nodes: [
            { id: '1', type: 'sheets', position: { x: 100, y: 100 }, data: { label: 'Google Sheets Input' } },
            { id: '2', type: 'ai', position: { x: 300, y: 100 }, data: { label: 'AI Processing' } },
            { id: '3', type: 'drive', position: { x: 500, y: 100 }, data: { label: 'Google Drive Output' } }
          ],
          edges: [
            { id: 'e1-2', source: '1', target: '2' },
            { id: 'e2-3', source: '2', target: '3' }
          ]
        },
        input_data: {
          sheets_id: 'demo-sheet-123',
          ai_prompt: 'Generate demo content',
          output_format: 'pdf'
        },
        created_by: 'demo_user'
      };

      const response = await fetch('http://localhost:8000/api/v1/workflow/instances', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(instanceData)
      });

      if (!response.ok) {
        throw new Error(`Failed to create demo instance: ${response.status}`);
      }

      const result = await response.json();
      const newInstanceId = result.instance_id;
      
      setDemoInstanceId(newInstanceId);
      setMessage(`✅ Demo workflow created! Instance ID: ${newInstanceId}`);
      
      // Auto-open execution monitor
      setTimeout(() => {
        showExecutionMonitor();
      }, 1000);
      
    } catch (error) {
      setMessage(`❌ Demo creation error: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`p-6 max-w-4xl mx-auto ${isDark ? 'bg-gray-900 text-gray-100' : 'bg-gray-50 text-gray-900'}`}>
      <div className={`rounded-lg shadow-lg p-6 ${isDark ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'}`}>
        <h1 className="text-3xl font-bold mb-6 text-center">
          🔗 Enhanced Logging System Demo
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <button
            onClick={runHealthCheck}
            disabled={isLoading}
            className={`p-4 rounded-lg font-medium transition-all duration-200 ${
              isDark 
                ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}`}
          >
            🩺 Check Backend Health
          </button>
          
          <button
            onClick={testLoggingEndpoints}
            disabled={isLoading}
            className={`p-4 rounded-lg font-medium transition-all duration-200 ${
              isDark 
                ? 'bg-green-600 hover:bg-green-700 text-white' 
                : 'bg-green-500 hover:bg-green-600 text-white'
            } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}`}
          >
            🧪 Test Logging APIs
          </button>
          
          <button
            onClick={showExecutionMonitor}
            disabled={isLoading}
            className={`p-4 rounded-lg font-medium transition-all duration-200 ${
              isDark 
                ? 'bg-purple-600 hover:bg-purple-700 text-white' 
                : 'bg-purple-500 hover:bg-purple-600 text-white'
            } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}`}
          >
            📊 Show Execution Monitor
          </button>
          
          <button
            onClick={createDemoWorkflow}
            disabled={isLoading}
            className={`p-4 rounded-lg font-medium transition-all duration-200 ${
              isDark 
                ? 'bg-orange-600 hover:bg-orange-700 text-white' 
                : 'bg-orange-500 hover:bg-orange-600 text-white'
            } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}`}
          >
            🚀 Create Demo Workflow
          </button>
        </div>

        <div className={`p-4 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
          <h3 className="font-semibold mb-2">Current Instance ID:</h3>
          <input
            type="text"
            value={demoInstanceId}
            onChange={(e) => setDemoInstanceId(e.target.value)}
            className={`w-full p-2 rounded border ${
              isDark 
                ? 'bg-gray-600 border-gray-500 text-gray-100' 
                : 'bg-white border-gray-300 text-gray-900'
            }`}
            placeholder="Enter workflow instance ID"
          />
        </div>

        {message && (
          <div className={`mt-4 p-4 rounded-lg ${
            message.includes('❌') 
              ? isDark ? 'bg-red-900/20 text-red-400' : 'bg-red-50 text-red-600'
              : isDark ? 'bg-green-900/20 text-green-400' : 'bg-green-50 text-green-600'
          }`}>
            <pre className="whitespace-pre-wrap font-mono text-sm">{message}</pre>
          </div>
        )}

        {isLoading && (
          <div className="mt-4 flex items-center justify-center">
            <div className={`animate-spin rounded-full h-8 w-8 border-b-2 ${
              isDark ? 'border-blue-400' : 'border-blue-600'
            }`}></div>
            <span className="ml-2">Processing...</span>
          </div>
        )}

        <div className={`mt-6 p-4 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
          <h3 className="font-semibold mb-2">📋 Integration Features:</h3>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center gap-2">
              <span className="text-green-500">✅</span>
              Enhanced Execution Panel with real-time logs
            </li>
            <li className="flex items-center gap-2">
              <span className="text-green-500">✅</span>
              Floating Monitor Button with activity indicators
            </li>
            <li className="flex items-center gap-2">
              <span className="text-green-500">✅</span>
              Backend logging API integration
            </li>
            <li className="flex items-center gap-2">
              <span className="text-green-500">✅</span>
              Real-time log streaming and updates
            </li>
            <li className="flex items-center gap-2">
              <span className="text-green-500">✅</span>
              Workflow execution monitoring
            </li>
            <li className="flex items-center gap-2">
              <span className="text-green-500">✅</span>
              Enhanced error tracking and analytics
            </li>
          </ul>
        </div>
      </div>

      {/* Enhanced Execution Panel */}
      <EnhancedExecutionPanel
        workflowInstanceId={demoInstanceId}
        onClose={executionMonitor.hidePanel}
        isVisible={executionMonitor.isVisible}
      />

      {/* Floating Monitor */}
      <FloatingExecutionMonitor position="bottom-right" />
    </div>
  );
};

export default LoggingDemo;
