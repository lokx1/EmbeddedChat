/**
 * Chat Service
 * Handles communication with AI providers through backend
 */
import { SendMessageRequest, ChatResponse, Message, AIProvider } from '../components/Chat/types';

class ChatService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
  }

  /**
   * Send message to AI provider
   */
  async sendMessage(request: SendMessageRequest): Promise<ChatResponse> {
    try {
      // Prepare the request payload
      const payload = {
        provider: request.provider,
        model: request.model,
        apiKey: request.apiKey,
        temperature: request.temperature,
        maxTokens: request.maxTokens,
        systemPrompt: request.systemPrompt,
        message: request.message,
        conversationId: request.conversationId,
        conversationHistory: this.formatConversationHistory(request.conversationHistory),
        attachedDocuments: request.attachedDocuments || []
      };

      // Prepare headers
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Add mock user header if needed (for testing)
      // In a real app, this would be handled by authentication middleware
      // headers['X-Mock-User-ID'] = '1';

      // Send request to backend
      const response = await fetch(`${this.baseUrl}/api/v1/chat/send`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        content: data.content || data.response || 'No response received',
        usage: data.usage,
        metadata: data.metadata
      };

    } catch (error) {
      console.error('Chat service error:', error);
      
      // If backend is not available, try direct AI provider call
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.log('Backend not available, trying direct AI provider...');
        return this.sendMessageDirect(request);
      }
      
      throw error;
    }
  }

  /**
   * Direct AI provider call (fallback when backend is not available)
   */
  private async sendMessageDirect(request: SendMessageRequest): Promise<ChatResponse> {
    switch (request.provider) {
      case 'openai':
        return this.callOpenAIDirect(request);
      case 'claude':
        return this.callClaudeDirect(request);
      case 'gemini':
        return this.callGeminiDirect(request);
      case 'ollama':
        return this.callOllamaDirect(request);
      default:
        throw new Error(`Unsupported provider: ${request.provider}`);
    }
  }

  /**
   * Direct OpenAI API call
   */
  private async callOpenAIDirect(request: SendMessageRequest): Promise<ChatResponse> {
    if (!request.apiKey) {
      throw new Error('OpenAI API key is required');
    }

    const messages = [
      { role: 'system', content: request.systemPrompt },
      ...this.formatConversationHistory(request.conversationHistory),
      { role: 'user', content: request.message }
    ];

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${request.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: request.model,
        messages,
        temperature: request.temperature,
        max_tokens: request.maxTokens,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: { message: 'Unknown error' } }));
      throw new Error(error.error?.message || `OpenAI API Error: ${response.status}`);
    }

    const data = await response.json();
    
    return {
      content: data.choices[0]?.message?.content || 'No response received',
      usage: {
        promptTokens: data.usage?.prompt_tokens,
        completionTokens: data.usage?.completion_tokens,
        totalTokens: data.usage?.total_tokens,
      }
    };
  }

  /**
   * Direct Claude API call
   */
  private async callClaudeDirect(request: SendMessageRequest): Promise<ChatResponse> {
    if (!request.apiKey) {
      throw new Error('Claude API key is required');
    }

    // Format messages for Claude
    const messages = this.formatConversationHistory(request.conversationHistory);
    messages.push({ role: 'user', content: request.message });

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': request.apiKey,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: request.model,
        max_tokens: request.maxTokens,
        temperature: request.temperature,
        system: request.systemPrompt,
        messages,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: { message: 'Unknown error' } }));
      throw new Error(error.error?.message || `Claude API Error: ${response.status}`);
    }

    const data = await response.json();
    
    return {
      content: data.content[0]?.text || 'No response received',
      usage: {
        promptTokens: data.usage?.input_tokens,
        completionTokens: data.usage?.output_tokens,
        totalTokens: (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0),
      }
    };
  }

  /**
   * Direct Gemini API call
   */
  private async callGeminiDirect(request: SendMessageRequest): Promise<ChatResponse> {
    if (!request.apiKey) {
      throw new Error('Gemini API key is required');
    }

    // Format conversation for Gemini
    const contents = [];
    
    // Add system prompt as first user message
    if (request.systemPrompt) {
      contents.push({
        role: 'user',
        parts: [{ text: `System: ${request.systemPrompt}` }]
      });
      contents.push({
        role: 'model',
        parts: [{ text: 'Understood. I will follow these instructions.' }]
      });
    }

    // Add conversation history
    for (const msg of request.conversationHistory) {
      contents.push({
        role: msg.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: msg.content }]
      });
    }

    // Add current message
    contents.push({
      role: 'user',
      parts: [{ text: request.message }]
    });

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${request.model}:generateContent?key=${request.apiKey}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents,
          generationConfig: {
            temperature: request.temperature,
            maxOutputTokens: request.maxTokens,
          },
        }),
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: { message: 'Unknown error' } }));
      throw new Error(error.error?.message || `Gemini API Error: ${response.status}`);
    }

    const data = await response.json();
    
    return {
      content: data.candidates[0]?.content?.parts[0]?.text || 'No response received',
      usage: {
        promptTokens: data.usageMetadata?.promptTokenCount,
        completionTokens: data.usageMetadata?.candidatesTokenCount,
        totalTokens: data.usageMetadata?.totalTokenCount,
      }
    };
  }

  /**
   * Direct Ollama API call
   */
  private async callOllamaDirect(request: SendMessageRequest): Promise<ChatResponse> {
    const messages = [
      { role: 'system', content: request.systemPrompt },
      ...this.formatConversationHistory(request.conversationHistory),
      { role: 'user', content: request.message }
    ];

    const response = await fetch('http://localhost:11434/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: request.model,
        messages,
        stream: false,
        options: {
          temperature: request.temperature,
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`Ollama API Error: ${response.status}. Make sure Ollama is running.`);
    }

    const data = await response.json();
    
    return {
      content: data.message?.content || 'No response received',
      usage: {
        promptTokens: data.prompt_eval_count,
        completionTokens: data.eval_count,
        totalTokens: (data.prompt_eval_count || 0) + (data.eval_count || 0),
      }
    };
  }

  /**
   * Format conversation history for API calls
   */
  private formatConversationHistory(history: Message[]): Array<{role: string, content: string}> {
    return history
      .filter(msg => msg.role !== 'system')
      .map(msg => ({
        role: msg.role === 'assistant' ? 'assistant' : 'user',
        content: msg.content
      }));
  }

  /**
   * Test API connection
   */
  async testConnection(provider: AIProvider, apiKey: string, model: string): Promise<boolean> {
    try {
      const testRequest: SendMessageRequest = {
        provider,
        model,
        apiKey,
        temperature: 0.1,
        maxTokens: 50,
        systemPrompt: '',
        message: 'Hello, please respond with just "OK" to test the connection.',
        conversationHistory: []
      };

      const response = await this.sendMessage(testRequest);
      return !!response.content;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }
}

export const chatService = new ChatService();
