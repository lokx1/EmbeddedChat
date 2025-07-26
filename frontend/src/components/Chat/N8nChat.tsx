import React, { useState, useRef, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';
import { ThinkingDisplay } from './ThinkingDisplay';
import { MemoryDisplay } from './MemoryDisplay';
import { FileUpload } from './FileUpload';
import { 
  DocumentTextIcon, 
  CpuChipIcon,
  ClockIcon,
  ChevronUpIcon
} from '@heroicons/react/24/outline';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  thinking?: string;
  attachments?: string[];
}

interface Memory {
  id: string;
  content: string;
  context: string;
  relevance_score: number;
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

export const N8nChat: React.FC = () => {
  const { isDark } = useTheme();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentThinking, setCurrentThinking] = useState('');
  const [showThinking, setShowThinking] = useState(false);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [summaries, setSummaries] = useState<ConversationSummary[]>([]);
  const [showMemoryPanel, setShowMemoryPanel] = useState(false);
  const [selectedModel, setSelectedModel] = useState('llama3.2');
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const conversationId = useRef<string>(`conv-${Date.now()}`);

  // Available models
  const availableModels = [
    { id: 'llama3.2', name: 'Llama 3.2', provider: 'ollama' },
    { id: 'llama3.1', name: 'Llama 3.1', provider: 'ollama' },
    { id: 'qwen2.5', name: 'Qwen 2.5', provider: 'ollama' },
    { id: 'mistral', name: 'Mistral', provider: 'ollama' },
    { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'anthropic' },
    { id: 'gpt-4', name: 'GPT-4', provider: 'openai' },
  ];

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, showThinking]);

  // Load memories on component mount
  useEffect(() => {
    loadMemories();
    loadSummaries();
  }, []);

  const loadMemories = async () => {
    try {
      const response = await fetch('/api/v1/memory');
      if (response.ok) {
        const data = await response.json();
        setMemories(data);
      }
    } catch (error) {
      console.error('Error loading memories:', error);
    }
  };

  const loadSummaries = async () => {
    try {
      const response = await fetch('/api/v1/memory/summaries');
      if (response.ok) {
        const data = await response.json();
        setSummaries(data);
      }
    } catch (error) {
      console.error('Error loading summaries:', error);
    }
  };

  const extractMemory = async (content: string, context: string) => {
    try {
      const response = await fetch('/api/v1/memory/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          context,
          conversation_id: conversationId.current,
        }),
      });
      
      if (response.ok) {
        loadMemories(); // Reload memories after extraction
      }
    } catch (error) {
      console.error('Error extracting memory:', error);
    }
  };

  const handleSendMessage = async (content: string, files?: File[]) => {
    if (!content.trim() && (!files || files.length === 0)) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      content,
      sender: 'user',
      timestamp: new Date(),
      attachments: files?.map(f => f.name),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setUploadedFiles([]);
    setIsLoading(true);
    setShowThinking(true);
    setCurrentThinking('');

    try {
      // Simulate streaming thinking process
      const thinkingSteps = [
        'Analyzing your request...',
        'Retrieving relevant information...',
        'Processing context and memories...',
        'Formulating response...',
      ];

      for (let i = 0; i < thinkingSteps.length; i++) {
        setCurrentThinking(thinkingSteps.slice(0, i + 1).join('\n'));
        await new Promise(resolve => setTimeout(resolve, 800));
      }

      // Send request to AI service
      const requestBody = {
        message: content,
        model: selectedModel,
        conversation_id: conversationId.current,
        files: files?.map(f => f.name) || [],
        stream: true,
      };

      const response = await fetch('/api/v1/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const fullThinking = currentThinking;
      setShowThinking(false);

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantContent = '';

      const assistantMessage: Message = {
        id: `msg-${Date.now()}-assistant`,
        content: '',
        sender: 'assistant',
        timestamp: new Date(),
        thinking: fullThinking,
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.content) {
                  assistantContent += data.content;
                  setMessages(prev => prev.map(msg => 
                    msg.id === assistantMessage.id 
                      ? { ...msg, content: assistantContent }
                      : msg
                  ));
                }
              } catch (e) {
                // Ignore JSON parse errors for malformed chunks
              }
            }
          }
        }
      }

      // Extract memory from the conversation
      const conversationContext = `User: ${content}\nAssistant: ${assistantContent}`;
      await extractMemory(assistantContent, conversationContext);

    } catch (error) {
      console.error('Error sending message:', error);
      setShowThinking(false);
      
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error`,
        content: 'Sorry, there was an error processing your request. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = (files: File[]) => {
    setUploadedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const clearChat = () => {
    setMessages([]);
    conversationId.current = `conv-${Date.now()}`;
  };

  return (
    <div className={`flex h-screen ${isDark ? 'bg-gray-900' : 'bg-white'}`}>
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className={`flex items-center justify-between p-4 border-b ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-gray-50'}`}>
          <div className="flex items-center gap-3">
            <CpuChipIcon className="w-6 h-6 text-blue-500" />
            <h1 className={`text-xl font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
              AI Assistant
            </h1>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Model Selector */}
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className={`px-3 py-1 text-sm border rounded-md ${
                isDark 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              }`}
            >
              {availableModels.map(model => (
                <option key={model.id} value={model.id}>
                  {model.name} ({model.provider})
                </option>
              ))}
            </select>

            {/* Memory Panel Toggle */}
            <button
              onClick={() => setShowMemoryPanel(!showMemoryPanel)}
              className={`p-2 rounded-md transition-colors ${
                showMemoryPanel
                  ? 'bg-blue-500 text-white'
                  : isDark
                    ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                    : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
              }`}
              title="Toggle Memory Panel"
            >
              <ClockIcon className="w-5 h-5" />
            </button>

            {/* Clear Chat */}
            <button
              onClick={clearChat}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                isDark
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-red-500 hover:bg-red-600 text-white'
              }`}
            >
              Clear Chat
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className={`text-center py-12 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
              <CpuChipIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg mb-2">Start a conversation</p>
              <p className="text-sm">Ask me anything, and I'll help you with detailed thinking and memory.</p>
            </div>
          )}

          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              showThinking={!!message.thinking}
            />
          ))}

          {/* Thinking Display */}
          {showThinking && (
            <ThinkingDisplay
              content={currentThinking}
              isVisible={showThinking}
            />
          )}

          {/* Typing Indicator */}
          {isLoading && !showThinking && <TypingIndicator />}

          <div ref={messagesEndRef} />
        </div>

        {/* File Upload Area */}
        {uploadedFiles.length > 0 && (
          <div className={`px-4 py-2 border-t ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-gray-50'}`}>
            <div className="flex flex-wrap gap-2">
              {uploadedFiles.map((file, index) => (
                <div
                  key={index}
                  className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
                    isDark ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  <DocumentTextIcon className="w-4 h-4" />
                  <span>{file.name}</span>
                  <button
                    onClick={() => removeFile(index)}
                    className="text-red-500 hover:text-red-600"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className={`p-4 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className="flex items-end gap-3">
            <FileUpload onFilesSelected={handleFileUpload} />
            <div className="flex-1">
              <MessageInput
                value={inputValue}
                onChange={setInputValue}
                onSend={(content) => handleSendMessage(content, uploadedFiles)}
                disabled={isLoading}
                placeholder="Type your message... (supports files and documents)"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Memory Panel */}
      {showMemoryPanel && (
        <div className={`w-80 border-l ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-gray-50'}`}>
          <div className="flex items-center justify-between p-4 border-b border-gray-300">
            <h2 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Memory & Context
            </h2>
            <button
              onClick={() => setShowMemoryPanel(false)}
              className={`p-1 rounded-md ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-200'}`}
            >
              <ChevronUpIcon className="w-5 h-5" />
            </button>
          </div>
          <MemoryDisplay 
            memories={memories}
            summaries={summaries}
            onRefresh={() => {
              loadMemories();
              loadSummaries();
            }}
          />
        </div>
      )}
    </div>
  );
};
