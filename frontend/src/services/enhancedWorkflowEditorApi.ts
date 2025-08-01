/**
 * Enhanced Workflow Editor API Service
 */

// Component metadata interfaces
export interface ComponentParameter {
  name: string;
  label: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'textarea' | 'file' | 'json';
  required: boolean;
  default_value?: any;
  description?: string;
  options?: Array<{ label: string; value: any }>;
  validation?: Record<string, any>;
}

export interface ComponentHandle {
  id: string;
  type: 'source' | 'target';
  position: 'top' | 'bottom' | 'left' | 'right';
  label?: string;
}

export interface WorkflowComponentMetadata {
  type: string;
  name: string;
  description: string;
  category: 'triggers' | 'data_sources' | 'ai_processing' | 'control_flow' | 'output_actions';
  icon: string;
  color: string;
  parameters: ComponentParameter[];
  input_handles: ComponentHandle[];
  output_handles: ComponentHandle[];
  is_trigger: boolean;
  is_async: boolean;
  max_runtime_seconds?: number;
}

// Execution interfaces
export interface ExecutionStatus {
  instance_id: string;
  status: 'draft' | 'running' | 'completed' | 'failed' | 'cancelled';
  is_running: boolean;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface ExecutionEvent {
  event_type: string;
  data: Record<string, any>;
  timestamp: string;
}

export interface ExecutionLog {
  id: string;
  step_name: string;
  status: string;
  created_at: string;
  execution_time_ms?: number;
  error_message?: string;
}

// Enhanced workflow interfaces (extending existing ones)
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
  viewport?: { x: number; y: number; zoom: number };
}

export interface SaveWorkflowRequest {
  name: string;
  description?: string;
  category?: string;
  workflow_data: WorkflowEditorData;
  is_public?: boolean;
}

export interface WorkflowInstance {
  id: string;
  name: string;
  description?: string;
  template_id?: string;
  workflow_data: WorkflowEditorData;
  status: string;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  error_message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  created_by?: string;
}

// Template interface (different from instance)
export interface WorkflowTemplate {
  id: string;
  name: string;
  description?: string;
  category?: string;
  is_public?: boolean;
  template_data?: WorkflowEditorData;
  workflow_data?: WorkflowEditorData; // Alias for backward compatibility
  created_at: string;
  updated_at?: string;
  created_by?: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

class EnhancedWorkflowEditorApi {
  private readonly baseUrl = 'http://localhost:8000/api/v1/workflow';

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'API request failed');
      }

      return data;
    } catch (error) {
      console.error('API request error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // Component Management
  async getComponents(category?: string): Promise<ApiResponse<WorkflowComponentMetadata[]>> {
    const params = category ? `?category=${category}` : '';
    return this.request(`/components${params}`);
  }

  async getComponentMetadata(componentType: string): Promise<ApiResponse<WorkflowComponentMetadata>> {
    return this.request(`/components/${componentType}`);
  }

  // Workflow Instance Management
  async createInstance(instanceData: Partial<WorkflowInstance>): Promise<ApiResponse<{ instance_id: string }>> {
    return this.request('/instances', {
      method: 'POST',
      body: JSON.stringify(instanceData),
    });
  }

  async getInstances(filters?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<{ instances: WorkflowInstance[] }>> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.limit) params.append('limit', String(filters.limit));
    if (filters?.offset) params.append('offset', String(filters.offset));

    const queryString = params.toString();
    return this.request(`/instances${queryString ? `?${queryString}` : ''}`);
  }

  async getInstance(instanceId: string): Promise<ApiResponse<{ instance: WorkflowInstance }>> {
    return this.request(`/instances/${instanceId}`);
  }

  // Workflow Execution
  async executeInstance(
    instanceId: string,
    inputData?: Record<string, any>
  ): Promise<ApiResponse<{ instance_id: string; status: string }>> {
    return this.request(`/instances/${instanceId}/execute`, {
      method: 'POST',
      body: JSON.stringify(inputData || {}),
    });
  }

  async stopExecution(instanceId: string): Promise<ApiResponse<{ instance_id: string }>> {
    return this.request(`/instances/${instanceId}/stop`, {
      method: 'POST',
    });
  }

  async getExecutionStatus(instanceId: string): Promise<ApiResponse<ExecutionStatus>> {
    return this.request(`/instances/${instanceId}/status`);
  }

  async getExecutionLogs(
    instanceId: string,
    limit = 100,
    offset = 0
  ): Promise<ApiResponse<{ logs: ExecutionLog[] }>> {
    return this.request(`/instances/${instanceId}/logs?limit=${limit}&offset=${offset}`);
  }

  // WebSocket connection for real-time updates
  connectToExecutionUpdates(instanceId: string): WebSocket {
    const wsUrl = `ws://localhost:8000/api/v1/workflow/ws/${instanceId}`;
    return new WebSocket(wsUrl);
  }

  // Editor-specific endpoints
  async saveWorkflow(request: SaveWorkflowRequest): Promise<ApiResponse<{ id: string }>> {
    return this.request('/editor/save', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async loadWorkflow(workflowId: string): Promise<ApiResponse<WorkflowInstance>> {
    return this.request(`/editor/load/${workflowId}`);
  }

  async listEditorWorkflows(filters?: {
    category?: string;
    is_public?: boolean;
  }): Promise<ApiResponse<{ workflows: WorkflowInstance[] }>> {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.is_public !== undefined) params.append('is_public', String(filters.is_public));

    const queryString = params.toString();
    return this.request(`/editor/list${queryString ? `?${queryString}` : ''}`);
  }
}

export const enhancedWorkflowEditorApi = new EnhancedWorkflowEditorApi();
export default enhancedWorkflowEditorApi;
