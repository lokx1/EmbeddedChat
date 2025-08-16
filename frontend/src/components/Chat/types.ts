/**
 * TypeScript types for Chat components
 */

export type AIProvider = 'openai' | 'claude' | 'gemini' | 'ollama';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  files?: MessageFile[];
  metadata?: {
    provider?: string;
    model?: string;
    usage?: {
      promptTokens?: number;
      completionTokens?: number;
      totalTokens?: number;
    };
  };
  isError?: boolean;
  isThinking?: boolean;
}

export interface MessageFile {
  name: string;
  size: number;
  type: string;
  url?: string;
}

export interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
  messageCount?: number;
  preview?: string;
}

export interface ChatSettings {
  provider: AIProvider;
  model: string;
  apiKey: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
}

export interface ChatResponse {
  content: string;
  usage?: {
    promptTokens?: number;
    completionTokens?: number;
    totalTokens?: number;
  };
  metadata?: Record<string, any>;
}

export interface SendMessageRequest {
  message: string;
  provider: AIProvider;
  model: string;
  apiKey: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
  conversationHistory: Message[];
  conversationId?: number;
  files?: File[];
  attachedDocuments?: number[];  // Document IDs to include in context
}

// Provider configurations
export const AI_PROVIDERS = {
  openai: {
    name: 'OpenAI',
    models: ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
    defaultModel: 'gpt-4o',
    keyPrefix: 'sk-',
    description: 'Most versatile AI model with excellent reasoning'
  },
  claude: {
    name: 'Anthropic Claude',
    models: ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307'],
    defaultModel: 'claude-3-5-sonnet-20241022',
    keyPrefix: 'sk-ant-',
    description: 'Excellent for analysis and creative writing'
  },
  gemini: {
    name: 'Google Gemini',
    models: ['gemini-2.5-flash', 'gemini-2.5-pro'],
    defaultModel: 'gemini-2.5-flash',
    keyPrefix: 'AI',
    description: 'Fast and efficient with good reasoning capabilities'
  },
  ollama: {
    name: 'Ollama (Local)',
    models: ['llama3.2', 'llama3.2:8b', 'mistral', 'codellama'],
    defaultModel: 'llama3.2',
    keyPrefix: '',
    description: 'Run AI models locally on your machine'
  }
} as const;

export type ProviderConfig = typeof AI_PROVIDERS[keyof typeof AI_PROVIDERS];
