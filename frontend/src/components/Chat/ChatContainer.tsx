/**
 * Modern Chat Container - Main chat interface
 * Design inspired by ChatGPT, Claude, and Gemini interfaces
 */
import { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ChatSidebar from './ChatSidebar';
import AIProviderSettings from './AIProviderSettings';
// import FileUpload from './FileUpload';
// import DocumentViewer from './DocumentViewer';
import { Message, ChatSettings, AIProvider } from './types';
import { chatService } from '../../services/chatService';
import { conversationService } from '../../services/conversationService';
import { documentService, Document } from '../../services/documentService';
import UserSwitcher from '../debug/UserSwitcher';

interface ChatContainerProps {
  className?: string;
}

export default function ChatContainer({ className = '' }: ChatContainerProps) {
  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<any[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  
  // Mock user state for testing
  const [currentUser, setCurrentUser] = useState({ 
    id: 1, 
    username: 'test_user', 
    email: 'test@example.com' 
  });
  
  // Chat settings with localStorage persistence
  const [chatSettings, setChatSettings] = useState<ChatSettings>(() => {
    // Load from localStorage if available
    try {
      const savedSettings = localStorage.getItem('chatSettings');
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        console.log('Chat settings loaded from localStorage:', parsed.provider); // Debug log
        return parsed;
      }
    } catch (error) {
      console.error('Failed to load chat settings:', error);
    }
    
    console.log('Using default chat settings: gemini'); // Debug log
    // Default settings
    return {
      provider: 'gemini',
      model: 'gemini-2.5-flash',
      apiKey: '',
      temperature: 0.7,
      maxTokens: 2000,
      systemPrompt: 'You are a helpful AI assistant.'
    };
  });

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Save settings to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem('chatSettings', JSON.stringify(chatSettings));
      console.log('Chat settings saved:', chatSettings.provider); // Debug log
    } catch (error) {
      console.error('Failed to save chat settings:', error);
    }
  }, [chatSettings]);

  // Load conversations on mount and when user changes
  useEffect(() => {
    loadConversations();
    // Clear current conversation and messages when user changes
    setCurrentConversationId(null);
    setMessages([]);
    // Keep settings persistent - don't reset them
  }, [currentUser.id]);

  // Load conversations from API
  const loadConversations = async () => {
    try {
      const conversations = await conversationService.getConversations(false, currentUser.id);
      setConversations(conversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
      // Fallback to empty array
      setConversations([]);
    }
  };

  // Create new conversation
  const createNewConversation = async () => {
    try {
      const newConversation = await conversationService.createConversation(chatSettings);
      setCurrentConversationId(newConversation.id);
      setMessages([]);
      setConversations(prev => [newConversation, ...prev]);
    } catch (error) {
      console.error('Failed to create conversation:', error);
      // Fallback to local conversation
      const newId = Date.now().toString();
      setCurrentConversationId(newId);
      setMessages([]);
    }
  };

  // Load specific conversation
  const loadConversation = async (conversationId: string) => {
    setCurrentConversationId(conversationId);
    try {
      const data = await conversationService.getConversation(conversationId);
      setMessages(data.messages);
      
      // Only update non-provider related settings from conversation
      // Keep user's preferred AI provider, model, and API key
      if (data.settings) {
        setChatSettings(prev => ({
          ...prev,
          // Only update these specific settings, preserve provider preferences
          temperature: data.settings.temperature ?? prev.temperature,
          maxTokens: data.settings.maxTokens ?? prev.maxTokens,
          systemPrompt: data.settings.systemPrompt ?? prev.systemPrompt
        }));
      }
    } catch (error) {
      console.error('Failed to load conversation:', error);
      setMessages([]);
    }
  };

  // Send message
  const handleSendMessage = async (content: string, files?: File[]) => {
    if (!content.trim() && !files?.length) return;

    // Validate AI provider settings
    if (!chatSettings.apiKey && chatSettings.provider !== 'ollama') {
      alert(`Please set your ${chatSettings.provider.toUpperCase()} API key in settings`);
      setSettingsOpen(true);
      return;
    }

    let uploadedDocumentIds: number[] = [];

    // If files are provided, upload them first
    if (files && files.length > 0) {
      try {
        console.log(`Uploading ${files.length} files...`);
        
        for (const file of files) {
          // Check if file type is supported
          if (!documentService.isSupportedFileType(file)) {
            alert(`File type ${file.type || 'unknown'} is not supported`);
            continue;
          }

          try {
            // Upload file with AI processing
            const uploadedDoc = await documentService.uploadFile(
              file,
              chatSettings.provider,
              chatSettings.apiKey
            );
            
            uploadedDocumentIds.push(uploadedDoc.id);
            setDocuments(prev => [uploadedDoc, ...prev]);
            
            console.log(`Uploaded: ${file.name} -> Document ID: ${uploadedDoc.id}`);
          } catch (uploadError) {
            console.error(`Failed to upload ${file.name}:`, uploadError);
            alert(`Failed to upload ${file.name}: ${uploadError instanceof Error ? uploadError.message : 'Unknown error'}`);
          }
        }
      } catch (error) {
        console.error('File upload error:', error);
        alert(`File upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        return;
      }
    }

    // Create user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content || (files?.length ? `Uploaded ${files.length} file(s) for analysis` : ''),
      timestamp: new Date(),
      files: files?.map(file => ({
        name: file.name,
        size: file.size,
        type: file.type
      }))
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send to AI service with attached documents
      const response = await chatService.sendMessage({
        message: content || `Please analyze the uploaded file(s)`,
        provider: chatSettings.provider as AIProvider,
        model: chatSettings.model,
        apiKey: chatSettings.apiKey,
        temperature: chatSettings.temperature,
        maxTokens: chatSettings.maxTokens,
        systemPrompt: chatSettings.systemPrompt,
        conversationHistory: messages,
        conversationId: currentConversationId ? parseInt(currentConversationId) : undefined,
        attachedDocuments: uploadedDocumentIds.length > 0 ? uploadedDocumentIds : undefined
      });

      // Create AI response message
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.content,
        timestamp: new Date(),
        metadata: {
          provider: chatSettings.provider,
          model: chatSettings.model,
          usage: response.usage
        }
      };

      setMessages(prev => [...prev, aiMessage]);

      // Update conversation title if it's the first message
      if (messages.length === 0 && currentConversationId) {
        const title = (content || 'File Analysis').length > 50 ? (content || 'File Analysis').substring(0, 50) + '...' : (content || 'File Analysis');
        setConversations(prev => 
          prev.map(conv => 
            conv.id === currentConversationId 
              ? { ...conv, title, updatedAt: new Date().toISOString() }
              : conv
          )
        );
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Create error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Delete conversation
  const handleDeleteConversation = async (conversationId: string) => {
    try {
      await conversationService.deleteConversation(conversationId);
      setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      
      // If deleting current conversation, clear it
      if (conversationId === currentConversationId) {
        setCurrentConversationId(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  // Rename conversation
  const handleRenameConversation = async (conversationId: string, newTitle: string) => {
    try {
      await conversationService.updateConversation(conversationId, { title: newTitle });
      setConversations(prev => 
        prev.map(conv => 
          conv.id === conversationId 
            ? { ...conv, title: newTitle, updatedAt: new Date().toISOString() }
            : conv
        )
      );
    } catch (error) {
      console.error('Failed to rename conversation:', error);
    }
  };

  // Update chat settings
  const handleSettingsUpdate = (newSettings: Partial<ChatSettings>) => {
    console.log('Updating chat settings with:', newSettings); // Debug log
    setChatSettings(prev => ({ ...prev, ...newSettings }));
  };

  // Debug function to check localStorage (can be called from browser console)
  (window as any).debugChatSettings = () => {
    const saved = localStorage.getItem('chatSettings');
    console.log('Current localStorage chatSettings:', saved ? JSON.parse(saved) : 'not found');
    console.log('Current state chatSettings:', chatSettings);
  };

  // Load user documents
  const loadDocuments = async () => {
    try {
      const result = await documentService.getDocuments();
      setDocuments(result.documents);
    } catch (error) {
      console.error('Failed to load documents:', error);
      setDocuments([]);
    }
  };

  // Load documents on mount and when user changes
  useEffect(() => {
    loadDocuments();
  }, [currentUser.id]);



  return (
    <div className={`flex h-full bg-gray-50 dark:bg-gray-900 ${className}`}>
      {/* Sidebar */}
      <ChatSidebar
        isOpen={sidebarOpen}
        conversations={conversations}
        currentConversationId={currentConversationId}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onNewConversation={createNewConversation}
        onSelectConversation={loadConversation}
        onOpenSettings={() => setSettingsOpen(true)}
        onDeleteConversation={handleDeleteConversation}
        onRenameConversation={handleRenameConversation}
      />

      {/* Chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              )}
              <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                {currentConversationId 
                  ? conversations.find(c => c.id === currentConversationId)?.title || 'Chat'
                  : 'EmbeddedChat AI'
                }
              </h1>
            </div>

            <div className="flex items-center gap-3">
              {/* User Switcher for Testing */}
              <UserSwitcher 
                currentUserId={currentUser.id}
                onUserChange={(user) => setCurrentUser(user)}
              />
              
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {chatSettings.provider.toUpperCase()} • {chatSettings.model}
              </span>
              
              {/* Documents count indicator */}
              {documents.length > 0 && (
                <div className="flex items-center space-x-1 text-sm text-gray-500 dark:text-gray-400">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>{documents.length}</span>
                </div>
              )}
              
              <button
                onClick={() => setSettingsOpen(true)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.5 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-hidden">
          <MessageList
            messages={messages}
            isLoading={isLoading}
            className="h-full"
          />
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
          <MessageInput
            onSendMessage={handleSendMessage}
            disabled={isLoading}
            placeholder={messages.length === 0 ? "Start a conversation..." : "Type your message..."}
          />
        </div>
      </div>



      {/* Settings Modal */}
      {settingsOpen && (
        <AIProviderSettings
          settings={chatSettings}
          onUpdate={handleSettingsUpdate}
          onClose={() => setSettingsOpen(false)}
        />
      )}
    </div>
  );
}