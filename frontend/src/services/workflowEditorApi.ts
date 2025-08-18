/**
 * API services for Workflow Editor
 */

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: {
    label: string;
    type: string;
    config?: Record<string, any>;
  };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface WorkflowEditorData {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  viewport?: Record<string, any>;
}

export interface SaveWorkflowRequest {
  name: string;
  description?: string;
  category?: string;
  workflow_data: WorkflowEditorData;
  is_public?: boolean;
}

export interface UpdateWorkflowRequest {
  name?: string;
  description?: string;
  category?: string;
  workflow_data?: WorkflowEditorData;
  is_public?: boolean;
}

export interface WorkflowEditorResponse {
  id: string;
  name: string;
  description?: string;
  category: string;
  workflow_data: WorkflowEditorData;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

const BASE_URL = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/workflow/editor`;

export const workflowEditorApi = {
  // Save a new workflow
  saveWorkflow: async (request: SaveWorkflowRequest): Promise<{ success: boolean; data: WorkflowEditorResponse; error?: string }> => {
    try {
      const response = await fetch(`${BASE_URL}/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save workflow');
      }

      const data = await response.json();
      return { success: true, data: data.data };
    } catch (error) {
      console.error('Error saving workflow:', error);
      return { 
        success: false, 
        data: {} as WorkflowEditorResponse, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  },

  // Load a workflow by ID
  loadWorkflow: async (workflowId: string): Promise<{ success: boolean; data: WorkflowEditorResponse; error?: string }> => {
    try {
      const response = await fetch(`${BASE_URL}/load/${workflowId}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load workflow');
      }

      const data = await response.json();
      return { success: true, data: data.data };
    } catch (error) {
      console.error('Error loading workflow:', error);
      return { 
        success: false, 
        data: {} as WorkflowEditorResponse, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  },

  // Update an existing workflow
  updateWorkflow: async (workflowId: string, request: UpdateWorkflowRequest): Promise<{ success: boolean; data: WorkflowEditorResponse; error?: string }> => {
    try {
      const response = await fetch(`${BASE_URL}/update/${workflowId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update workflow');
      }

      const data = await response.json();
      return { success: true, data: data.data };
    } catch (error) {
      console.error('Error updating workflow:', error);
      return { 
        success: false, 
        data: {} as WorkflowEditorResponse, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  },

  // Delete a workflow
  deleteWorkflow: async (workflowId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${BASE_URL}/delete/${workflowId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete workflow');
      }

      return { success: true };
    } catch (error) {
      console.error('Error deleting workflow:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  },

  // List workflows
  listWorkflows: async (options?: { category?: string; is_public?: boolean }): Promise<{ success: boolean; data: Omit<WorkflowEditorResponse, 'workflow_data'>[]; error?: string }> => {
    try {
      const params = new URLSearchParams();
      if (options?.category) params.append('category', options.category);
      if (options?.is_public !== undefined) params.append('is_public', options.is_public.toString());

      const response = await fetch(`${BASE_URL}/list?${params.toString()}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to list workflows');
      }

      const data = await response.json();
      return { success: true, data: data.data.workflows };
    } catch (error) {
      console.error('Error listing workflows:', error);
      return { 
        success: false, 
        data: [], 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  },
};
