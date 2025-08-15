import { API_CONFIG, API_ENDPOINTS, apiRequest, testAPIConnection } from '../config';

export class ApiService {
  private static instance: ApiService;
  private isConnected = false;
  private currentEndpoint = '';

  private constructor() {}

  static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  async initialize(): Promise<boolean> {
    try {
      const result = await testAPIConnection();
      this.isConnected = result.success;
      this.currentEndpoint = result.endpoint || API_CONFIG.BASE_URL;
      
      if (this.isConnected) {
        console.log('✅ ApiService initialized successfully');
      } else {
        console.error('❌ ApiService initialization failed');
      }
      
      return this.isConnected;
    } catch (error) {
      console.error('❌ ApiService initialization error:', error);
      this.isConnected = false;
      return false;
    }
  }

  // Health check
  async healthCheck() {
    try {
      return await apiRequest(API_ENDPOINTS.HEALTH);
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  // Authentication
  async login(credentials: { username: string; password: string }) {
    try {
      return await apiRequest(API_ENDPOINTS.LOGIN, {
        method: 'POST',
        body: JSON.stringify(credentials),
      });
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  async register(userData: { username: string; email: string; password: string }) {
    try {
      return await apiRequest(API_ENDPOINTS.REGISTER, {
        method: 'POST',
        body: JSON.stringify(userData),
      });
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  // Chat
  async sendMessage(message: string, conversationId?: string) {
    try {
      return await apiRequest(API_ENDPOINTS.CHAT, {
        method: 'POST',
        body: JSON.stringify({ message, conversationId }),
      });
    } catch (error) {
      console.error('Send message failed:', error);
      throw error;
    }
  }

  async getChatHistory(conversationId?: string) {
    try {
      const endpoint = conversationId 
        ? `${API_ENDPOINTS.CHAT_HISTORY}/${conversationId}`
        : API_ENDPOINTS.CHAT_HISTORY;
      return await apiRequest(endpoint);
    } catch (error) {
      console.error('Get chat history failed:', error);
      throw error;
    }
  }

  // Documents
  async uploadDocument(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      return await apiRequest(API_ENDPOINTS.UPLOAD, {
        method: 'POST',
        body: formData,
        headers: {}, // Remove Content-Type to let browser set it for FormData
      });
    } catch (error) {
      console.error('Document upload failed:', error);
      throw error;
    }
  }

  async getDocuments() {
    try {
      return await apiRequest(API_ENDPOINTS.DOCUMENTS);
    } catch (error) {
      console.error('Get documents failed:', error);
      throw error;
    }
  }

  // Dashboard
  async getDashboardStats() {
    try {
      return await apiRequest(API_ENDPOINTS.STATS);
    } catch (error) {
      console.error('Get dashboard stats failed:', error);
      throw error;
    }
  }

  // Workflow
  async getWorkflows() {
    try {
      return await apiRequest(API_ENDPOINTS.WORKFLOW);
    } catch (error) {
      console.error('Get workflows failed:', error);
      throw error;
    }
  }

  async executeWorkflow(workflowId: string, data?: any) {
    try {
      return await apiRequest(API_ENDPOINTS.WORKFLOW_EXECUTE, {
        method: 'POST',
        body: JSON.stringify({ workflowId, data }),
      });
    } catch (error) {
      console.error('Execute workflow failed:', error);
      throw error;
    }
  }

  // Utility methods
  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  getCurrentEndpoint(): string {
    return this.currentEndpoint;
  }

  async reconnect(): Promise<boolean> {
    return await this.initialize();
  }
}

// Export singleton instance
export const apiService = ApiService.getInstance();

// Export for React components
export default apiService; 