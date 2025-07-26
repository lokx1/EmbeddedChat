import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { CpuChipIcon } from '@heroicons/react/24/outline';

export const TypingIndicator: React.FC = () => {
  const { isDark } = useTheme();

  return (
    <div className="flex gap-3 justify-start">
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isDark ? 'bg-blue-600' : 'bg-blue-500'
      }`}>
        <CpuChipIcon className="w-5 h-5 text-white" />
      </div>
      
      <div className={`max-w-2xl p-4 rounded-2xl ${
        isDark
          ? 'bg-gray-800 text-gray-100 border border-gray-700'
          : 'bg-gray-100 text-gray-900 border border-gray-200'
      }`}>
        <div className="flex items-center gap-2">
          <div className="flex space-x-1">
            <div className={`w-2 h-2 ${isDark ? 'bg-gray-400' : 'bg-gray-600'} rounded-full animate-bounce`}></div>
            <div className={`w-2 h-2 ${isDark ? 'bg-gray-400' : 'bg-gray-600'} rounded-full animate-bounce`} style={{ animationDelay: '0.1s' }}></div>
            <div className={`w-2 h-2 ${isDark ? 'bg-gray-400' : 'bg-gray-600'} rounded-full animate-bounce`} style={{ animationDelay: '0.2s' }}></div>
          </div>
          <span className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            AI is typing...
          </span>
        </div>
      </div>
    </div>
  );
};
