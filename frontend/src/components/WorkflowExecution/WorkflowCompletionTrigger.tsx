/**
 * Workflow Completion Trigger - Load logs when workflow finishes execution
 */
import React, { useCallback } from 'react';
import { useExecutionMonitor } from '../../hooks/useExecutionMonitor';

interface WorkflowCompletionTriggerProps {
  onWorkflowComplete?: (instanceId: string) => void;
}

export const WorkflowCompletionTrigger: React.FC<WorkflowCompletionTriggerProps> = ({
  onWorkflowComplete
}) => {
  const { loadWorkflowLogs, showPanel } = useExecutionMonitor();

  // Function to call when workflow execution completes
  const handleWorkflowCompletion = useCallback(async (instanceId: string) => {
    console.log(`Workflow ${instanceId} completed - loading logs...`);
    
    // Load logs for the completed workflow
    await loadWorkflowLogs(instanceId);
    
    // Show the execution panel with the logs
    showPanel(instanceId);
    
    // Call optional callback
    if (onWorkflowComplete) {
      onWorkflowComplete(instanceId);
    }
  }, [loadWorkflowLogs, showPanel, onWorkflowComplete]);

  // Export the handler for external use
  React.useImperativeHandle(undefined, () => ({
    triggerWorkflowCompletion: handleWorkflowCompletion
  }));

  return null; // This is a logical component, no UI
};

// Hook to use the workflow completion trigger
export const useWorkflowCompletion = () => {
  const { loadWorkflowLogs, showPanel } = useExecutionMonitor();

  const triggerWorkflowCompletion = useCallback(async (instanceId: string) => {
    console.log(`Workflow ${instanceId} completed - loading logs...`);
    
    // Load logs for the completed workflow
    await loadWorkflowLogs(instanceId);
    
    // Show the execution panel with the logs
    showPanel(instanceId);
    
    // Optional: Show a toast notification
    console.log(`Workflow execution logs loaded for instance: ${instanceId}`);
  }, [loadWorkflowLogs, showPanel]);

  return {
    triggerWorkflowCompletion
  };
};

export default WorkflowCompletionTrigger;
