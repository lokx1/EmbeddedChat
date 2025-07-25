// API service for dashboard statistics and data
const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface DashboardStats {
  activeChats: number;
  totalDocuments: number;
  totalWorkflows: number;
  teamMembers: number;
  chatGrowth: string;
  documentGrowth: string;
  workflowGrowth: string;
  memberGrowth: string;
}

export interface RecentActivityItem {
  id: string;
  type: 'chat' | 'document' | 'workflow' | 'error';
  title: string;
  description: string;
  timestamp: string;
  status: 'success' | 'error' | 'warning' | 'info';
  userId?: number;
  userName?: string;
}

class DashboardService {
  private async fetchWithAuth(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('auth_token');
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async getDashboardStats(): Promise<DashboardStats> {
    try {
      console.log('DashboardService: Fetching stats from', `${API_BASE_URL}/dashboard/stats`);
      const response = await this.fetchWithAuth('/dashboard/stats');
      console.log('DashboardService: Raw API response:', response);
      
      // Convert snake_case to camelCase
      const stats: DashboardStats = {
        activeChats: response.active_chats || 0,
        totalDocuments: response.total_documents || 0,
        totalWorkflows: response.total_workflows || 0,
        teamMembers: response.team_members || 1,
        chatGrowth: response.chat_growth || 'No data',
        documentGrowth: response.document_growth || 'No data',
        workflowGrowth: response.workflow_growth || 'No data',
        memberGrowth: response.member_growth || 'No change',
      };
      
      console.log('DashboardService: Converted stats:', stats);
      return stats;
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
      // Return mock data as fallback
      const fallbackStats = {
        activeChats: 0,
        totalDocuments: 0,
        totalWorkflows: 0,
        teamMembers: 1,
        chatGrowth: 'No data',
        documentGrowth: 'No data',
        workflowGrowth: 'No data',
        memberGrowth: 'No change',
      };
      console.log('DashboardService: Using fallback stats:', fallbackStats);
      return fallbackStats;
    }
  }

  async getRecentActivity(): Promise<RecentActivityItem[]> {
    try {
      console.log('DashboardService: Fetching activity from', `${API_BASE_URL}/dashboard/activity`);
      const response = await this.fetchWithAuth('/dashboard/activity');
      console.log('DashboardService: Activity response:', response);
      return response;
    } catch (error) {
      console.error('Failed to fetch recent activity:', error);
      // Return empty array as fallback
      console.log('DashboardService: Using empty activity array as fallback');
      return [];
    }
  }

  async getUserSessions(): Promise<any[]> {
    try {
      const response = await this.fetchWithAuth('/chat/sessions');
      return response;
    } catch (error) {
      console.error('Failed to fetch user sessions:', error);
      return [];
    }
  }

  async getDocuments(): Promise<any[]> {
    try {
      const response = await this.fetchWithAuth('/documents');
      return response;
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      return [];
    }
  }
}

export const dashboardService = new DashboardService();
