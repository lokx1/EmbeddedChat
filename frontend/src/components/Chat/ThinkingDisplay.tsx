import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

interface ThinkingDisplayProps {
  content?: string;
  isVisible?: boolean;
}

export const ThinkingDisplay: React.FC<ThinkingDisplayProps> = ({ 
  content = "", 
  isVisible = true 
}) => {
  const { isDark } = useTheme();
  const [isExpanded, setIsExpanded] = useState(false);

  if (!isVisible) return null;

  const hasContent = content && content.trim().length > 0;

  return (
    <div className={`mb-4 ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-gray-50 border-gray-200'} border rounded-lg overflow-hidden`}>
      {/* Header */}
      <div 
        className={`flex items-center justify-between p-3 cursor-pointer hover:${isDark ? 'bg-gray-750' : 'bg-gray-100'} transition-colors`}
        onClick={() => hasContent && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          {hasContent ? (
            isExpanded ? (
              <ChevronDownIcon className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronRightIcon className="w-4 h-4 text-gray-500" />
            )
          ) : (
            <div className="w-4 h-4 flex items-center justify-center">
              <div className="w-2 h-2 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}
          <span className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
            {hasContent ? 'Thinking' : 'Thinking...'}
          </span>
        </div>
        {hasContent && (
          <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
            Click to {isExpanded ? 'collapse' : 'expand'}
          </span>
        )}
      </div>

      {/* Content */}
      {hasContent && isExpanded && (
        <div className={`px-3 pb-3 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'} whitespace-pre-wrap font-mono text-xs leading-relaxed`}>
            {content}
          </div>
        </div>
      )}

      {/* Loading animation when no content */}
      {!hasContent && (
        <div className={`px-3 pb-3 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className="flex items-center gap-2">
            <div className="flex space-x-1">
              <div className={`w-1.5 h-1.5 ${isDark ? 'bg-gray-500' : 'bg-gray-400'} rounded-full animate-bounce`}></div>
              <div className={`w-1.5 h-1.5 ${isDark ? 'bg-gray-500' : 'bg-gray-400'} rounded-full animate-bounce`} style={{ animationDelay: '0.1s' }}></div>
              <div className={`w-1.5 h-1.5 ${isDark ? 'bg-gray-500' : 'bg-gray-400'} rounded-full animate-bounce`} style={{ animationDelay: '0.2s' }}></div>
            </div>
            <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
              Analyzing your request...
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
