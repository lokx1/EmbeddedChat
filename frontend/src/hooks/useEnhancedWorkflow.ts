/**
 * Enhanced hooks for workflow editor and execution management
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { Node, Edge } from 'reactflow';
import enhancedWorkflowEditorApi, {
  WorkflowComponentMetadata,
  WorkflowInstance,
  ExecutionStatus,
  ExecutionEvent,
  ExecutionLog,
  WorkflowEditorData,
  SaveWorkflowRequest,
} from '../services/enhancedWorkflowEditorApi';

// Hook for managing workflow components
export const useWorkflowComponents = () => {
  const [components, setComponents] = useState<WorkflowComponentMetadata[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchComponents = useCallback(async (category?: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await enhancedWorkflowEditorApi.getComponents(category);
      if (response.success && response.data) {
        setComponents(response.data);
      } else {
        setError(response.error || 'Failed to fetch components');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const getComponentMetadata = useCallback(async (componentType: string) => {
    try {
      const response = await enhancedWorkflowEditorApi.getComponentMetadata(componentType);
      return response;
    } catch (err) {
      console.error('Error fetching component metadata:', err);
      return { success: false, error: err instanceof Error ? err.message : 'Unknown error' };
    }
  }, []);

  useEffect(() => {
    fetchComponents();
  }, [fetchComponents]);

  return {
    components,
    loading,
    error,
    fetchComponents,
    getComponentMetadata,
  };
};

// Hook for managing workflow instances
export const useWorkflowInstances = () => {
  const [instances, setInstances] = useState<WorkflowInstance[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInstances = useCallback(async (filters?: {
    status?: string;
    limit?: number;
    offset?: number;
  }) => {
    setLoading(true);
    setError(null);

    try {
      const response = await enhancedWorkflowEditorApi.getInstances(filters);
      if (response.success && response.data) {
        setInstances(response.data.instances);
      } else {
        setError(response.error || 'Failed to fetch instances');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const createInstance = useCallback(async (instanceData: Partial<WorkflowInstance>) => {
    setLoading(true);
    setError(null);

    try {
      const response = await enhancedWorkflowEditorApi.createInstance(instanceData);
      if (response.success) {
        await fetchInstances(); // Refresh list
        return response;
      } else {
        setError(response.error || 'Failed to create instance');
        return response;
      }
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  }, [fetchInstances]);

  const getInstance = useCallback(async (instanceId: string) => {
    try {
      const response = await enhancedWorkflowEditorApi.getInstance(instanceId);
      return response;
    } catch (err) {
      console.error('Error fetching instance:', err);
      return { success: false, error: err instanceof Error ? err.message : 'Unknown error' };
    }
  }, []);

  return {
    instances,
    loading,
    error,
    fetchInstances,
    createInstance,
    getInstance,
  };
};

// Hook for workflow execution with real-time updates
export const useWorkflowExecution = () => {
  const [executionStatus, setExecutionStatus] = useState<ExecutionStatus | null>(null);
  const [executionLogs, setExecutionLogs] = useState<ExecutionLog[]>([]);
  const [executionEvents, setExecutionEvents] = useState<ExecutionEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);

  // Connect to WebSocket for real-time updates
  const connectToUpdates = useCallback((targetInstanceId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }

    try {
      const ws = enhancedWorkflowEditorApi.connectToExecutionUpdates(targetInstanceId);
      
      ws.onopen = () => {
        console.log('WebSocket connected for execution updates');
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const executionEvent: ExecutionEvent = JSON.parse(event.data);
          
          // Add to events list
          setExecutionEvents(prev => [executionEvent, ...prev.slice(0, 99)]); // Keep last 100 events
          
          // Update status based on event type
          if (executionEvent.event_type === 'execution_started') {
            setExecutionStatus(prev => prev ? { ...prev, status: 'running', is_running: true } : null);
          } else if (executionEvent.event_type === 'execution_completed') {
            setExecutionStatus(prev => prev ? { ...prev, status: 'completed', is_running: false } : null);
          } else if (executionEvent.event_type === 'execution_failed') {
            setExecutionStatus(prev => prev ? { 
              ...prev, 
              status: 'failed', 
              is_running: false,
              error_message: executionEvent.data.error 
            } : null);
          } else if (executionEvent.event_type === 'execution_stopped') {
            setExecutionStatus(prev => prev ? { ...prev, status: 'cancelled', is_running: false } : null);
          }
          
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
      };

      wsRef.current = ws;
      
    } catch (err) {
      console.error('Error connecting to WebSocket:', err);
      setError('Failed to connect to real-time updates');
    }
  }, []);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  // Execute workflow
  const executeWorkflow = useCallback((targetInstanceId: string, inputData?: Record<string, any>) => {
    setLoading(true);
    setError(null);

    return enhancedWorkflowEditorApi.executeInstance(targetInstanceId, inputData)
      .then(response => {
        if (response.success) {
          // No automatic WebSocket connection - user can manually connect if needed
          console.log(`Workflow execution started for instance: ${targetInstanceId} - no auto-connection`);
          return response;
        } else {
          setError(response.error || 'Failed to execute workflow');
          return response;
        }
      })
      .catch(err => {
        const error = err instanceof Error ? err.message : 'Unknown error';
        setError(error);
        return { success: false, error };
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  // Stop execution
  const stopExecution = useCallback((targetInstanceId: string) => {
    setLoading(true);
    setError(null);

    return enhancedWorkflowEditorApi.stopExecution(targetInstanceId)
      .then(response => {
        if (response.success) {
          return response;
        } else {
          setError(response.error || 'Failed to stop execution');
          return response;
        }
      })
      .catch(err => {
        const error = err instanceof Error ? err.message : 'Unknown error';
        setError(error);
        return { success: false, error };
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  // Fetch execution status
  const fetchExecutionStatus = useCallback(async (targetInstanceId: string) => {
    try {
      const response = await enhancedWorkflowEditorApi.getExecutionStatus(targetInstanceId);
      if (response.success && response.data) {
        setExecutionStatus(response.data);
      }
      return response;
    } catch (err) {
      console.error('Error fetching execution status:', err);
      return { success: false, error: err instanceof Error ? err.message : 'Unknown error' };
    }
  }, []);

  // Fetch execution logs
  const fetchExecutionLogs = useCallback(async (targetInstanceId: string, limit = 100, offset = 0) => {
    try {
      const response = await enhancedWorkflowEditorApi.getExecutionLogs(targetInstanceId, limit, offset);
      if (response.success && response.data) {
        setExecutionLogs(response.data.logs);
      }
      return response;
    } catch (err) {
      console.error('Error fetching execution logs:', err);
      return { success: false, error: err instanceof Error ? err.message : 'Unknown error' };
    }
  }, []);

  // Manual connection only - no auto-connect
  // Users must manually connect when needed
  useEffect(() => {
    // No automatic connection - everything is manual
    console.log('useWorkflowExecution initialized - no auto-connection');
    
    return () => {
      // Always disconnect on cleanup
      disconnect();
    };
  }, [disconnect]);

  return {
    executionStatus,
    executionLogs,
    executionEvents,
    isConnected,
    loading,
    error,
    executeWorkflow,
    stopExecution,
    fetchExecutionStatus,
    fetchExecutionLogs,
    connectToUpdates,
    disconnect,
  };
};

// Hook for saving and loading workflows
export const useWorkflowEditor = () => {
  const [currentWorkflow, setCurrentWorkflow] = useState<WorkflowInstance | null>(null);
  const [availableWorkflows, setAvailableWorkflows] = useState<WorkflowInstance[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const saveWorkflow = useCallback(async (workflowData: SaveWorkflowRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await enhancedWorkflowEditorApi.saveWorkflow(workflowData);
      if (response.success) {
        // Refresh available workflows
        await fetchAvailableWorkflows();
        return response;
      } else {
        setError(response.error || 'Failed to save workflow');
        return response;
      }
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  }, []);

  const loadWorkflow = useCallback(async (workflowId: string) => {
    console.log('loadWorkflow called with ID:', workflowId);
    setLoading(true);
    setError(null);

    try {
      console.log('Calling API to load workflow...');
      const response = await enhancedWorkflowEditorApi.loadWorkflow(workflowId);
      console.log('API response:', response);
      if (response.success && response.data) {
        console.log('Setting current workflow:', response.data);
        setCurrentWorkflow(response.data);
        return response;
      } else {
        console.log('Load failed:', response.error);
        setError(response.error || 'Failed to load workflow');
        return response;
      }
    } catch (err) {
      console.log('Load error:', err);
      const error = err instanceof Error ? err.message : 'Unknown error';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchAvailableWorkflows = useCallback(async (filters?: {
    category?: string;
    is_public?: boolean;
  }) => {
    setLoading(true);
    setError(null);

    try {
      const response = await enhancedWorkflowEditorApi.listEditorWorkflows(filters);
      if (response.success && response.data) {
        setAvailableWorkflows(response.data.workflows);
      } else {
        setError(response.error || 'Failed to fetch workflows');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  // Helper function to convert React Flow data to our format
  const convertReactFlowData = useCallback((nodes: Node[], edges: Edge[], viewport?: { x: number; y: number; zoom: number }): WorkflowEditorData => {
    return {
      nodes: nodes.map(node => ({
        id: node.id,
        type: node.type || 'default',
        position: node.position,
        data: {
          label: node.data?.label || '',
          type: node.data?.type || node.type || 'default',
          config: node.data?.config || {}
        }
      })),
      edges: edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle || undefined,
        targetHandle: edge.targetHandle || undefined
      })),
      viewport
    };
  }, []);

  useEffect(() => {
    fetchAvailableWorkflows();
  }, [fetchAvailableWorkflows]);

  return {
    currentWorkflow,
    availableWorkflows,
    loading,
    error,
    saveWorkflow,
    loadWorkflow,
    fetchAvailableWorkflows,
    convertReactFlowData,
    setCurrentWorkflow,
  };
};
