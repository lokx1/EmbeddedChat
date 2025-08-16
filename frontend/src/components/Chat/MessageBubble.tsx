/**
 * Modern Message Bubble Component
 * Design inspired by ChatGPT and Claude interfaces
 */
import { useState } from 'react';
import { Message } from './types';
import { formatDistanceToNow } from 'date-fns';

interface MessageBubbleProps {
  message: Message;
  className?: string;
}

export default function MessageBubble({ message, className = '' }: MessageBubbleProps) {
  const [showTimestamp, setShowTimestamp] = useState(false);
  const isUser = message.role === 'user';
  const isError = message.isError;

  // Format message content (basic markdown support)
  const formatContent = (content: string) => {
    // Basic markdown formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 dark:bg-gray-700 px-1 rounded text-sm">$1</code>')
      .replace(/\n/g, '<br/>');
  };

  // Copy message content
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      // TODO: Show success toast
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  return (
    <div className={`group relative ${className}`}>
      <div 
        className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
        onMouseEnter={() => setShowTimestamp(true)}
        onMouseLeave={() => setShowTimestamp(false)}
      >
        <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-3`}>
          {/* Avatar */}
          <div className="flex-shrink-0">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              isUser 
                ? 'bg-blue-500 text-white' 
                : isError
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-600 dark:bg-gray-400 text-white dark:text-gray-900'
            }`}>
              {isUser ? (
                'U'
              ) : isError ? (
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              )}
            </div>
          </div>

          {/* Message Content */}
          <div className={`relative ${isUser ? 'text-right' : 'text-left'}`}>
            {/* Message Bubble */}
            <div className={`inline-block p-4 rounded-2xl ${
              isUser 
                ? 'bg-blue-500 text-white rounded-br-md' 
                : isError
                  ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 rounded-bl-md'
                  : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100 rounded-bl-md shadow-sm'
            }`}>
              {/* Message Text */}
              <div 
                className={`prose prose-sm max-w-none ${
                  isUser 
                    ? 'prose-invert' 
                    : 'prose-gray dark:prose-invert'
                }`}
                dangerouslySetInnerHTML={{ __html: formatContent(message.content) }}
              />

              {/* File Attachments */}
              {message.files && message.files.length > 0 && (
                <div className="mt-3 space-y-2">
                  {message.files.map((file, index) => (
                    <div 
                      key={index}
                      className={`flex items-center gap-2 p-2 rounded-lg ${
                        isUser 
                          ? 'bg-blue-400/20' 
                          : 'bg-gray-100 dark:bg-gray-700'
                      }`}
                    >
                      <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm">{file.name}</span>
                      <span className="text-xs opacity-75">({(file.size / 1024).toFixed(1)} KB)</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Metadata (for AI responses) */}
              {!isUser && message.metadata && (
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                  <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                    <span>{message.metadata.provider?.toUpperCase()}</span>
                    {message.metadata.model && (
                      <>
                        <span>•</span>
                        <span>{message.metadata.model}</span>
                      </>
                    )}
                    {message.metadata.usage?.totalTokens && (
                      <>
                        <span>•</span>
                        <span>{message.metadata.usage.totalTokens} tokens</span>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Timestamp */}
            {showTimestamp && (
              <div className={`mt-1 text-xs text-gray-500 dark:text-gray-400 ${
                isUser ? 'text-right' : 'text-left'
              }`}>
                {formatDistanceToNow(message.timestamp, { addSuffix: true })}
              </div>
            )}

            {/* Action Buttons */}
            <div className={`absolute top-0 ${
              isUser ? 'left-0 -translate-x-full' : 'right-0 translate-x-full'
            } flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200`}>
              <button
                onClick={copyToClipboard}
                className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                title="Copy message"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
              
              {!isUser && (
                <button
                  className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                  title="Regenerate response"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}