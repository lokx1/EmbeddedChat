/**
 * Message List Component
 * Displays conversation messages with auto-scroll and loading states
 */
import { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import { Message } from './types';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  className?: string;
}

export default function MessageList({ messages, isLoading = false, className = '' }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <div 
      ref={scrollRef}
      className={`flex-1 overflow-y-auto scroll-smooth ${className}`}
    >
      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Welcome Message */}
        {messages.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
              Welcome to EmbeddedChat AI
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
              Start a conversation with your AI assistant. You can ask questions, get help with tasks, 
              or have a casual chat.
            </p>
            
            {/* Suggested prompts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
              {[
                "Help me write a professional email",
                "Explain quantum computing in simple terms", 
                "Create a marketing strategy outline",
                "Review this code for improvements"
              ].map((prompt, index) => (
                <button
                  key={index}
                  className="p-3 text-left text-sm text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-blue-300 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-colors"
                  onClick={() => {
                    // TODO: Set input value to this prompt
                    console.log('Selected prompt:', prompt);
                  }}
                >
                  <span className="block font-medium mb-1">{prompt.split(' ').slice(0, 3).join(' ')}</span>
                  <span className="text-gray-500 dark:text-gray-400">{prompt}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="space-y-1">
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
            />
          ))}
        </div>

        {/* Typing Indicator */}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="flex max-w-[85%] gap-3">
              {/* AI Avatar */}
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-gray-600 dark:bg-gray-400 flex items-center justify-center text-sm font-medium text-white dark:text-gray-900">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>

              {/* Typing Bubble */}
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-md shadow-sm p-4">
                <TypingIndicator />
              </div>
            </div>
          </div>
        )}

        {/* Scroll to bottom spacer */}
        <div className="h-4" />
      </div>
    </div>
  );
}