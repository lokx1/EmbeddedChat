/**
 * Enhanced Logging Service - Connect Frontend to Backend Logging API
 */

export interface WorkflowTaskLog {
  id: string;
  task_id: string;
  task_name: string;
  task_type?: string;
  status?: 'success' | 'failed' | 'processing';
  log_level?: 'info' | 'warning' | 'error' | 'debug';
  
  // Input/Output tracking
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  expected_output?: Record<string, any>;
  
  // Success/Failure details
  success_criteria?: Record<string, any>;
  failure_reason?: string;
  error_code?: string;
  error_stack_trace?: string;
  
  // Performance metrics
  execution_time_ms?: number;
  memory_usage_mb?: number;
  cpu_usage_percent?: number;
  
  // Metadata
  workflow_instance_id?: string;
  user_id?: string;
  session_id?: string;
  metadata?: Record<string, any>;
  
  // Timestamps
  created_at: string;
  updated_at?: string;
}

export interface WorkflowExecutionStep {
  id: string;
  workflow_instance_id: string;
  step_name: string;
  step_order: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  
  // Step details
  step_type?: string;
  step_config?: Record<string, any>;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  
  // Execution metrics
  execution_time_ms?: number;
  memory_usage_mb?: number;
  error_message?: string;
  error_code?: string;
  
  // Analytics fields
  retry_count?: number;
  retry_limit?: number;
  parent_step_id?: string;
  dependencies_met?: boolean;
  
  // Timestamps
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface LogSummary {
  total_task_logs: number;
  total_execution_steps: number;
  status: string;
  success_rate?: number;
  average_execution_time?: number;
  most_common_errors?: string[];
  active_workflows?: number;
}

export interface LogQueryParams {
  workflow_instance_id?: string;
  task_type?: string;
  status?: string;
  log_level?: string;
  user_id?: string;
  limit?: number;
  offset?: number;
  start_date?: string;
  end_date?: string;
}

class EnhancedLoggingService {
  private baseUrl: string;
  private apiUrl: string;

  constructor() {
    this.baseUrl = 'http://localhost:8000';
    this.apiUrl = `${this.baseUrl}/api/v1/workflow/logs`;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<{
    success: boolean;
    data?: T;
    error?: string;
  }> {
    try {
      const response = await fetch(`${this.apiUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Enhanced Logging API request error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Get workflow task logs with filtering and pagination
   */
  async getTaskLogs(params?: LogQueryParams): Promise<{
    success: boolean;
    data?: WorkflowTaskLog[];
    error?: string;
  }> {
    const queryParams = new URLSearchParams();
    
    if (params?.workflow_instance_id) queryParams.append('workflow_instance_id', params.workflow_instance_id);
    if (params?.task_type) queryParams.append('task_type', params.task_type);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.log_level) queryParams.append('log_level', params.log_level);
    if (params?.user_id) queryParams.append('user_id', params.user_id);
    if (params?.limit) queryParams.append('limit', String(params.limit));
    if (params?.offset) queryParams.append('offset', String(params.offset));
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);

    const queryString = queryParams.toString();
    const endpoint = `/tasks${queryString ? `?${queryString}` : ''}`;
    
    return this.request<WorkflowTaskLog[]>(endpoint);
  }

  /**
   * Get workflow execution steps with filtering and pagination
   */
  async getExecutionSteps(params?: LogQueryParams): Promise<{
    success: boolean;
    data?: WorkflowExecutionStep[];
    error?: string;
  }> {
    const queryParams = new URLSearchParams();
    
    if (params?.workflow_instance_id) queryParams.append('workflow_instance_id', params.workflow_instance_id);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.limit) queryParams.append('limit', String(params.limit));
    if (params?.offset) queryParams.append('offset', String(params.offset));
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);

    const queryString = queryParams.toString();
    const endpoint = `/steps${queryString ? `?${queryString}` : ''}`;
    
    return this.request<WorkflowExecutionStep[]>(endpoint);
  }

  /**
   * Get logging summary and analytics
   */
  async getLogSummary(): Promise<{
    success: boolean;
    data?: LogSummary;
    error?: string;
  }> {
    return this.request<LogSummary>('/summary');
  }

  /**
   * Get detailed logs for a specific workflow instance
   */
  async getInstanceLogs(instanceId: string): Promise<{
    success: boolean;
    data?: {
      instance: any;
      task_logs: WorkflowTaskLog[];
      execution_steps: WorkflowExecutionStep[];
      summary: any;
    };
    error?: string;
  }> {
    return this.request<any>(`/instances/${instanceId}/detailed`);
  }

  /**
   * Fetch logs for a completed workflow instance (on-demand, not real-time)
   */
  async fetchWorkflowLogs(instanceId: string): Promise<{
    taskLogs: WorkflowTaskLog[];
    executionSteps: WorkflowExecutionStep[];
    success: boolean;
    error?: string;
  }> {
    try {
      const [taskLogsResult, stepsResult] = await Promise.all([
        this.getTaskLogs({ workflow_instance_id: instanceId }),
        this.getExecutionSteps({ workflow_instance_id: instanceId })
      ]);

      return {
        taskLogs: taskLogsResult.success ? taskLogsResult.data || [] : [],
        executionSteps: stepsResult.success ? stepsResult.data || [] : [],
        success: taskLogsResult.success && stepsResult.success,
        error: !taskLogsResult.success ? 'Failed to fetch task logs' : 
               !stepsResult.success ? 'Failed to fetch execution steps' : undefined
      };
    } catch (error) {
      console.error('Error fetching workflow logs:', error);
      return {
        taskLogs: [],
        executionSteps: [],
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Subscribe to workflow completion events (for future implementation)
   * For now, this is a placeholder that doesn't do continuous polling
   */
  async subscribeToWorkflowCompletion(
    _callback: (instanceId: string) => void
  ): Promise<() => void> {
    // Future: This could listen to WebSocket events for workflow completion
    // For now, it's just a placeholder that does nothing
    console.log('Workflow completion subscription set up (placeholder)');
    
    // Return cleanup function
    return () => {
      console.log('Workflow completion subscription cleaned up');
    };
  }

  /**
   * Health check for logging service
   */
  async healthCheck(): Promise<{
    success: boolean;
    data?: { status: string; timestamp: string };
    error?: string;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/health`);
      
      return {
        success: response.ok,
        data: { 
          status: response.ok ? 'healthy' : 'unhealthy',
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Health check failed'
      };
    }
  }
}

// Create singleton instance
export const enhancedLoggingService = new EnhancedLoggingService();

// React hook for using enhanced logging
export const useEnhancedLogging = () => {
  return {
    getTaskLogs: enhancedLoggingService.getTaskLogs.bind(enhancedLoggingService),
    getExecutionSteps: enhancedLoggingService.getExecutionSteps.bind(enhancedLoggingService),
    getLogSummary: enhancedLoggingService.getLogSummary.bind(enhancedLoggingService),
    getInstanceLogs: enhancedLoggingService.getInstanceLogs.bind(enhancedLoggingService),
    fetchWorkflowLogs: enhancedLoggingService.fetchWorkflowLogs.bind(enhancedLoggingService),
    subscribeToWorkflowCompletion: enhancedLoggingService.subscribeToWorkflowCompletion.bind(enhancedLoggingService),
    healthCheck: enhancedLoggingService.healthCheck.bind(enhancedLoggingService),
  };
};
