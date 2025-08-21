/**
 * Workflow API Service
 * Handles all workflow-related API calls to the backend
 */

export interface WorkflowTemplate {
  id: string;
  name: string;
  description?: string;
  template_data: any;
  category?: string;
  is_public: boolean;
  created_at: string;
  updated_at?: string;
}

export interface WorkflowInstance {
  id: string;
  name: string;
  template_id?: string;
  workflow_data: any;
  input_data?: any;
  output_data?: any;
  status: 'draft' | 'running' | 'completed' | 'failed';
  error_message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface WorkflowTaskLog {
  id: string;
  task_id: string;
  sheet_id?: string;
  status: string;
  input_description?: string;
  output_format?: string;
  model_specification?: string;
  processing_time_ms?: number;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

class WorkflowApiService {
  private baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
  private apiUrl = `${this.baseUrl}/api/v1/workflow`;

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.apiUrl}${endpoint}`, {
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

  // Template Methods
  async createTemplate(templateData: Partial<WorkflowTemplate>): Promise<ApiResponse<{ template_id: string }>> {
    return this.request('/templates', {
      method: 'POST',
      body: JSON.stringify(templateData),
    });
  }

  async getTemplates(filters?: {
    category?: string;
    is_public?: boolean;
  }): Promise<ApiResponse<{ templates: WorkflowTemplate[] }>> {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.is_public !== undefined) params.append('is_public', String(filters.is_public));
    
    const queryString = params.toString();
    return this.request(`/templates${queryString ? `?${queryString}` : ''}`);
  }

  async getTemplate(templateId: string): Promise<ApiResponse<{ template: WorkflowTemplate }>> {
    return this.request(`/templates/${templateId}`);
  }

  // Instance Methods
  async createInstance(instanceData: Partial<WorkflowInstance>): Promise<ApiResponse<{ instance_id: string }>> {
    return this.request('/instances', {
      method: 'POST',
      body: JSON.stringify(instanceData),
    });
  }

  async executeInstance(instanceId: string): Promise<ApiResponse<{ instance_id: string; status: string }>> {
    return this.request(`/instances/${instanceId}/execute`, {
      method: 'POST',
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

  // Google Sheets Processing
  async processGoogleSheets(data: {
    google_sheets_id: string;
    notification_settings?: any;
    output_settings?: any;
  }): Promise<ApiResponse<{ sheets_id: string }>> {
    return this.request('/google-sheets/process', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Reports
  async generateDailyReport(reportDate?: string): Promise<ApiResponse<{ report_date: string }>> {
    return this.request('/reports/daily', {
      method: 'POST',
      body: JSON.stringify({ report_date: reportDate }),
    });
  }

  // Analytics
  async getDailyAnalytics(date: string): Promise<ApiResponse<any>> {
    return this.request(`/analytics/daily?date=${date}`);
  }

  async getWeeklyAnalytics(endDate: string): Promise<ApiResponse<any>> {
    return this.request(`/analytics/weekly?end_date=${endDate}`);
  }

  // Task Logs
  async getTaskLogs(filters?: {
    limit?: number;
    offset?: number;
    status?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<ApiResponse<{ logs: WorkflowTaskLog[] }>> {
    const params = new URLSearchParams();
    if (filters?.limit) params.append('limit', String(filters.limit));
    if (filters?.offset) params.append('offset', String(filters.offset));
    if (filters?.status) params.append('status', filters.status);
    if (filters?.start_date) params.append('start_date', filters.start_date);
    if (filters?.end_date) params.append('end_date', filters.end_date);
    
    const queryString = params.toString();
    return this.request(`/task-logs${queryString ? `?${queryString}` : ''}`);
  }

  // Health Check
  async healthCheck(): Promise<ApiResponse<{ status: string }>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/workflow/health`);
      const data = await response.json();
      return { success: response.ok, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Health check failed',
      };
    }
  }
}

export const workflowApi = new WorkflowApiService();
export default workflowApi;
