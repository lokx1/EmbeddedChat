/**
 * Conversation Service
 * Handles conversation management API calls
 */
import { Conversation, ChatSettings } from '../components/Chat/types';

class ConversationService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
  }

  /**
   * Get all conversations for current user
   */
  async getConversations(includeArchived = false, userId?: number): Promise<Conversation[]> {
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      // Add mock user header for testing
      if (userId) {
        headers['X-Mock-User-ID'] = userId.toString();
      }
      
      const response = await fetch(
        `${this.baseUrl}/api/v1/chat/conversations?include_archived=${includeArchived}`,
        {
          method: 'GET',
          headers,
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return data.conversations.map((conv: any) => ({
        id: conv.id.toString(),
        title: conv.title,
        updatedAt: conv.updatedAt,
        messageCount: conv.messageCount,
        preview: '', // Can be populated from first message if needed
      }));

    } catch (error) {
      console.error('Failed to get conversations:', error);
      throw error;
    }
  }

  /**
   * Create a new conversation
   */
  async createConversation(settings: ChatSettings): Promise<Conversation> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'New Chat',
          provider: settings.provider,
          model: settings.model,
          systemPrompt: settings.systemPrompt,
          temperature: settings.temperature,
          maxTokens: settings.maxTokens,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        id: data.id.toString(),
        title: data.title,
        updatedAt: data.updatedAt,
        messageCount: data.messageCount,
        preview: '',
      };

    } catch (error) {
      console.error('Failed to create conversation:', error);
      throw error;
    }
  }

  /**
   * Get a specific conversation with messages
   */
  async getConversation(conversationId: string) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/conversations/${conversationId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        conversation: {
          id: data.id.toString(),
          title: data.title,
          updatedAt: data.updatedAt,
          messageCount: data.messageCount,
        },
        settings: {
          provider: data.provider,
          model: data.model,
          apiKey: '', // Don't return API key from server
          systemPrompt: data.systemPrompt,
          temperature: data.temperature,
          maxTokens: data.maxTokens,
        },
        messages: data.messages.map((msg: any) => ({
          id: msg.id.toString(),
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.createdAt),
          metadata: msg.usage ? {
            provider: msg.aiProvider,
            model: msg.aiModel,
            usage: msg.usage,
          } : undefined,
        })),
      };

    } catch (error) {
      console.error('Failed to get conversation:', error);
      throw error;
    }
  }

  /**
   * Update conversation
   */
  async updateConversation(conversationId: string, updates: any): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/conversations/${conversationId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      console.error('Failed to update conversation:', error);
      throw error;
    }
  }

  /**
   * Delete conversation
   */
  async deleteConversation(conversationId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      console.error('Failed to delete conversation:', error);
      throw error;
    }
  }

  /**
   * Archive conversation
   */
  async archiveConversation(conversationId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/conversations/${conversationId}/archive`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      console.error('Failed to archive conversation:', error);
      throw error;
    }
  }

  /**
   * Search conversations
   */
  async searchConversations(query: string): Promise<Conversation[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/v1/chat/conversations/search?q=${encodeURIComponent(query)}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return data.conversations.map((conv: any) => ({
        id: conv.id.toString(),
        title: conv.title,
        updatedAt: conv.updatedAt,
        messageCount: conv.messageCount,
        preview: '',
      }));

    } catch (error) {
      console.error('Failed to search conversations:', error);
      throw error;
    }
  }

  /**
   * Get chat statistics
   */
  async getChatStats() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Failed to get chat stats:', error);
      throw error;
    }
  }
}

export const conversationService = new ConversationService();
