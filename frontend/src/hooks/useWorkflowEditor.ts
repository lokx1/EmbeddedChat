/**
 * React hooks for Workflow Editor
 */
import { useState, useCallback } from 'react';
import { 
  workflowEditorApi, 
  SaveWorkflowRequest, 
  UpdateWorkflowRequest, 
  WorkflowEditorResponse,
  WorkflowEditorData 
} from '../services/workflowEditorApi';

export const useWorkflowEditor = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentWorkflow, setCurrentWorkflow] = useState<WorkflowEditorResponse | null>(null);
  const [workflows, setWorkflows] = useState<Omit<WorkflowEditorResponse, 'workflow_data'>[]>([]);

  // Save workflow
  const saveWorkflow = useCallback(async (request: SaveWorkflowRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await workflowEditorApi.saveWorkflow(request);
      
      if (result.success) {
        setCurrentWorkflow(result.data);
        // Refresh workflows list
        await listWorkflows();
        return { success: true, data: result.data };
      } else {
        setError(result.error || 'Failed to save workflow');
        return { success: false, error: result.error };
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  // Load workflow
  const loadWorkflow = useCallback(async (workflowId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await workflowEditorApi.loadWorkflow(workflowId);
      
      if (result.success) {
        setCurrentWorkflow(result.data);
        return { success: true, data: result.data };
      } else {
        setError(result.error || 'Failed to load workflow');
        return { success: false, error: result.error };
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  // Update workflow
  const updateWorkflow = useCallback(async (workflowId: string, request: UpdateWorkflowRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await workflowEditorApi.updateWorkflow(workflowId, request);
      
      if (result.success) {
        setCurrentWorkflow(result.data);
        // Refresh workflows list
        await listWorkflows();
        return { success: true, data: result.data };
      } else {
        setError(result.error || 'Failed to update workflow');
        return { success: false, error: result.error };
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  // Delete workflow
  const deleteWorkflow = useCallback(async (workflowId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await workflowEditorApi.deleteWorkflow(workflowId);
      
      if (result.success) {
        // Clear current workflow if it was deleted
        if (currentWorkflow?.id === workflowId) {
          setCurrentWorkflow(null);
        }
        // Refresh workflows list
        await listWorkflows();
        return { success: true };
      } else {
        setError(result.error || 'Failed to delete workflow');
        return { success: false, error: result.error };
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [currentWorkflow]);

  // List workflows
  const listWorkflows = useCallback(async (options?: { category?: string; is_public?: boolean }) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await workflowEditorApi.listWorkflows(options);
      
      if (result.success) {
        setWorkflows(result.data);
        return { success: true, data: result.data };
      } else {
        setError(result.error || 'Failed to list workflows');
        return { success: false, error: result.error };
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  // Create new workflow
  const createNewWorkflow = useCallback(() => {
    const newWorkflow: WorkflowEditorData = {
      nodes: [
        {
          id: '1',
          type: 'input',
          position: { x: 100, y: 100 },
          data: { label: 'Start', type: 'start' }
        }
      ],
      edges: [],
      viewport: { x: 0, y: 0, zoom: 1 }
    };

    setCurrentWorkflow({
      id: '',
      name: 'New Workflow',
      description: '',
      category: 'custom',
      workflow_data: newWorkflow,
      is_public: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    });

    return newWorkflow;
  }, []);

  // Clear current workflow
  const clearCurrentWorkflow = useCallback(() => {
    setCurrentWorkflow(null);
    setError(null);
  }, []);

  return {
    // State
    loading,
    error,
    currentWorkflow,
    workflows,
    
    // Actions
    saveWorkflow,
    loadWorkflow,
    updateWorkflow,
    deleteWorkflow,
    listWorkflows,
    createNewWorkflow,
    clearCurrentWorkflow,
    
    // Utils
    setCurrentWorkflow,
    setError
  };
};
