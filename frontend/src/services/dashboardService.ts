// Dashboard API service
interface DashboardStats {
  total_conversations: number;
  total_messages: number;
  total_documents: number;
  total_users: number;
  active_conversations_today: number;
  messages_today: number;
  avg_messages_per_conversation: number;
  most_active_day: string;
  ai_providers_status: any;
}

interface ActivityData {
  date: string;
  conversations: number;
  messages: number;
  documents_uploaded: number;
}

interface SystemHealth {
  overall_status: string;
  components: {
    database: { status: string; error?: string };
    ai_service: any;
    system_resources: {
      memory_usage_percent: number;
      cpu_usage_percent: number;
      disk_usage_percent: number;
      status: string;
    };
  };
}

interface ConversationStats {
  id: string;
  title: string;
  message_count: number;
  last_activity: string;
  duration_minutes?: number;
  ai_provider_used?: string;
  has_documents: boolean;
}

interface AIProviderStats {
  provider: string;
  status: string;
  total_requests: number;
  avg_response_time: number;
  success_rate: number;
  models_available: number;
  last_used?: string;
}

export class DashboardService {
  private baseUrl = '/api/v1/dashboard';

  async getStats(days: number = 30): Promise<DashboardStats> {
    const response = await fetch(`${this.baseUrl}/stats?days=${days}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }
    return response.json();
  }

  async getActivity(days: number = 30): Promise<{ activity_data: ActivityData[] }> {
    const response = await fetch(`${this.baseUrl}/activity?days=${days}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch activity: ${response.statusText}`);
    }
    return response.json();
  }

  async getSystemHealth(): Promise<SystemHealth> {
    const response = await fetch(`${this.baseUrl}/system-health`);
    if (!response.ok) {
      throw new Error(`Failed to fetch system health: ${response.statusText}`);
    }
    return response.json();
  }

  async getRecentConversations(limit: number = 20): Promise<{ conversations: ConversationStats[] }> {
    const response = await fetch(`${this.baseUrl}/conversations?limit=${limit}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch conversations: ${response.statusText}`);
    }
    return response.json();
  }

  async getAIProviderStats(): Promise<{ providers: AIProviderStats[] }> {
    const response = await fetch(`${this.baseUrl}/ai-providers`);
    if (!response.ok) {
      throw new Error(`Failed to fetch AI provider stats: ${response.statusText}`);
    }
    return response.json();
  }

  async exportConversations(format: 'json' | 'csv' = 'json', days: number = 30): Promise<any> {
    const response = await fetch(`${this.baseUrl}/export/conversations?format=${format}&days=${days}`);
    if (!response.ok) {
      throw new Error(`Failed to export conversations: ${response.statusText}`);
    }
    return response.json();
  }

  // Real-time dashboard updates
  async startRealTimeUpdates(callback: (data: any) => void): Promise<() => void> {
    const eventSource = new EventSource(`${this.baseUrl}/realtime`);
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        callback(data);
      } catch (error) {
        console.error('Error parsing real-time data:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('Real-time connection error:', error);
    };

    // Return cleanup function
    return () => {
      eventSource.close();
    };
  }
}

// Memory API service
interface Memory {
  id: string;
  content: string;
  context: string;
  relevance_score?: number;
  created_at: string;
  conversation_id?: string;
}

interface ConversationSummary {
  id: string;
  summary: string;
  key_points: string[];
  created_at: string;
  conversation_id: string;
}

export class MemoryService {
  private baseUrl = '/api/v1/memory';

  async getMemories(): Promise<Memory[]> {
    const response = await fetch(this.baseUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch memories: ${response.statusText}`);
    }
    return response.json();
  }

  async getSummaries(): Promise<ConversationSummary[]> {
    const response = await fetch(`${this.baseUrl}/summaries`);
    if (!response.ok) {
      throw new Error(`Failed to fetch summaries: ${response.statusText}`);
    }
    return response.json();
  }

  async createMemory(memory: Omit<Memory, 'id' | 'created_at'>): Promise<Memory> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(memory),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create memory: ${response.statusText}`);
    }
    return response.json();
  }

  async updateMemory(id: string, updates: Partial<Memory>): Promise<Memory> {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update memory: ${response.statusText}`);
    }
    return response.json();
  }

  async deleteMemory(id: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete memory: ${response.statusText}`);
    }
  }

  async extractMemory(content: string, context: string, conversationId?: string): Promise<Memory> {
    const response = await fetch(`${this.baseUrl}/extract`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        context,
        conversation_id: conversationId,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to extract memory: ${response.statusText}`);
    }
    return response.json();
  }
}

// AI Service API
export class AIService {
  private baseUrl = '/api/v1/ai';

  async getProviders(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/providers`);
    if (!response.ok) {
      throw new Error(`Failed to fetch providers: ${response.statusText}`);
    }
    return response.json();
  }

  async getModels(): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/models`);
    if (!response.ok) {
      throw new Error(`Failed to fetch models: ${response.statusText}`);
    }
    return response.json();
  }

  async getHealth(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Failed to fetch AI health: ${response.statusText}`);
    }
    return response.json();
  }

  async chat(request: {
    message: string;
    model?: string;
    provider?: string;
    conversation_id?: string;
    stream?: boolean;
    temperature?: number;
    max_tokens?: number;
    files?: string[];
    context?: string;
  }): Promise<Response> {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to send chat: ${response.statusText}`);
    }
    
    return response;
  }

  async getThinking(request: {
    message: string;
    provider?: string;
    context?: string;
  }): Promise<{ thinking_steps: string[] }> {
    const response = await fetch(`${this.baseUrl}/thinking`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get thinking: ${response.statusText}`);
    }
    return response.json();
  }
}

// Export service instances
export const dashboardService = new DashboardService();
export const memoryService = new MemoryService();
export const aiService = new AIService();
