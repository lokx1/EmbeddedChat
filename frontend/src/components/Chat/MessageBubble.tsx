import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { UserIcon, CpuChipIcon, ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  thinking?: string;
  attachments?: string[];
}

interface MessageBubbleProps {
  message: Message;
  showThinking?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, showThinking = false }) => {
  const { isDark } = useTheme();
  const [showThinkingContent, setShowThinkingContent] = useState(false);
  const isUser = message.sender === 'user';

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isDark ? 'bg-blue-600' : 'bg-blue-500'
        }`}>
          <CpuChipIcon className="w-5 h-5 text-white" />
        </div>
      )}
      
      <div className={`max-w-2xl ${isUser ? 'order-first' : ''}`}>
        {/* Thinking Display (only for assistant messages) */}
        {!isUser && message.thinking && showThinking && (
          <div className="mb-2">
            <div 
              className={`flex items-center gap-2 cursor-pointer p-2 rounded-lg ${
                isDark ? 'bg-gray-800 hover:bg-gray-750' : 'bg-gray-100 hover:bg-gray-200'
              } transition-colors`}
              onClick={() => setShowThinkingContent(!showThinkingContent)}
            >
              {showThinkingContent ? (
                <ChevronDownIcon className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronRightIcon className="w-4 h-4 text-gray-500" />
              )}
              <span className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                Thinking process
              </span>
            </div>
            
            {showThinkingContent && (
              <div className={`mt-2 p-3 rounded-lg border ${
                isDark ? 'bg-gray-800 border-gray-700' : 'bg-gray-50 border-gray-200'
              }`}>
                <pre className={`text-xs font-mono whitespace-pre-wrap ${
                  isDark ? 'text-gray-400' : 'text-gray-600'
                }`}>
                  {message.thinking}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* Message Content */}
        <div
          className={`p-4 rounded-2xl ${
            isUser
              ? 'bg-blue-500 text-white'
              : isDark
                ? 'bg-gray-800 text-gray-100 border border-gray-700'
                : 'bg-gray-100 text-gray-900 border border-gray-200'
          }`}
        >
          {/* Attachments */}
          {message.attachments && message.attachments.length > 0 && (
            <div className="mb-3">
              <div className="flex flex-wrap gap-2">
                {message.attachments.map((attachment, index) => (
                  <div
                    key={index}
                    className={`flex items-center gap-1 px-2 py-1 rounded-md text-xs ${
                      isUser
                        ? 'bg-blue-400 bg-opacity-50'
                        : isDark
                          ? 'bg-gray-700'
                          : 'bg-gray-200'
                    }`}
                  >
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                    </svg>
                    <span>{attachment}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Message Text */}
          <div className="prose prose-sm max-w-none">
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>
          </div>

          {/* Timestamp */}
          <div className={`text-xs mt-2 opacity-70 ${isUser ? 'text-right' : 'text-left'}`}>
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>

      {isUser && (
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isDark ? 'bg-gray-600' : 'bg-gray-400'
        }`}>
          <UserIcon className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
