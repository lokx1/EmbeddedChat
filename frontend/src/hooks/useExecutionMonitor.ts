/**
 * Hook for managing Execution Panel state and workflow monitoring
 * Updated to load logs on-demand instead of continuous polling
 */
import { useState, useEffect, useCallback } from 'react';
import { useEnhancedLogging, WorkflowTaskLog, WorkflowExecutionStep } from '../services/enhancedLoggingService';

export interface ExecutionMonitorState {
  isVisible: boolean;
  workflowInstanceId: string | null;
  isConnected: boolean;
  lastUpdate: Date | null;
  hasNewActivity: boolean;
}

export const useExecutionMonitor = () => {
  const [state, setState] = useState<ExecutionMonitorState>({
    isVisible: false,
    workflowInstanceId: null,
    isConnected: false,
    lastUpdate: null,
    hasNewActivity: false
  });

  const [recentLogs, setRecentLogs] = useState<(WorkflowTaskLog | WorkflowExecutionStep)[]>([]);

  const { healthCheck, fetchWorkflowLogs } = useEnhancedLogging();

  // Mark new activity
  const markNewActivity = useCallback(() => {
    setState(prev => ({
      ...prev,
      hasNewActivity: !prev.isVisible, // Only mark as new if panel is not visible
      lastUpdate: new Date()
    }));
  }, []);

  // Load logs for a specific workflow instance
  const loadWorkflowLogs = useCallback(async (instanceId: string) => {
    try {
      const result = await fetchWorkflowLogs(instanceId);
      if (result.success) {
        // Combine task logs and execution steps for display
        const combinedLogs = [
          ...result.taskLogs,
          ...result.executionSteps
        ].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        
        setRecentLogs(combinedLogs.slice(0, 20)); // Keep only the 20 most recent
        markNewActivity();
      }
    } catch (error) {
      console.error('Failed to load workflow logs:', error);
    }
  }, [fetchWorkflowLogs, markNewActivity]);

  // Check connection status
  const checkConnection = useCallback(async () => {
    try {
      const result = await healthCheck();
      setState(prev => ({
        ...prev,
        isConnected: result.success
      }));
      return result.success;
    } catch (error) {
      setState(prev => ({
        ...prev,
        isConnected: false
      }));
      return false;
    }
  }, [healthCheck]);

  // Show execution panel
  const showPanel = useCallback((instanceId?: string) => {
    setState(prev => ({
      ...prev,
      isVisible: true,
      workflowInstanceId: instanceId || null,
      hasNewActivity: false
    }));
  }, []);

  // Hide execution panel
  const hidePanel = useCallback(() => {
    setState(prev => ({
      ...prev,
      isVisible: false
    }));
  }, []);

  // Toggle panel visibility
  const togglePanel = useCallback(() => {
    setState(prev => ({
      ...prev,
      isVisible: !prev.isVisible,
      hasNewActivity: prev.isVisible ? false : prev.hasNewActivity
    }));
  }, []);

  // Set workflow instance to monitor
  const setWorkflowInstance = useCallback((instanceId: string | null) => {
    setState(prev => ({
      ...prev,
      workflowInstanceId: instanceId
    }));
  }, []);

  // Initialize connection check - no automatic polling  
  useEffect(() => {
    // Only check connection once when component mounts - no auto summary loading
    checkConnection();

    // No background intervals - everything is manual or on-demand
    console.log('ExecutionMonitor initialized - no background polling');

  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-hide new activity indicator after 5 seconds if panel is visible
  useEffect(() => {
    if (state.isVisible && state.hasNewActivity) {
      const timeout = setTimeout(() => {
        setState(prev => ({
          ...prev,
          hasNewActivity: false
        }));
      }, 5000);

      return () => clearTimeout(timeout);
    }
  }, [state.isVisible, state.hasNewActivity]);

  return {
    // State
    ...state,
    recentLogs,
    
    // Actions
    showPanel,
    hidePanel,
    togglePanel,
    setWorkflowInstance,
    checkConnection,
    loadWorkflowLogs, // New method to load logs on-demand
    
    // Utils
    getActivityCount: () => recentLogs.length,
    getLatestActivity: () => recentLogs[0] || null,
    isMonitoringWorkflow: () => !!state.workflowInstanceId
  };
};
