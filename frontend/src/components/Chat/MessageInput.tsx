import React, { useRef, KeyboardEvent } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { PaperAirplaneIcon } from '@heroicons/react/24/outline';

interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: (content: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  value,
  onChange,
  onSend,
  disabled = false,
  placeholder = 'Type your message...'
}) => {
  const { isDark } = useTheme();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (value.trim() && !disabled) {
      onSend(value.trim());
      onChange('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
    
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  };

  return (
    <div className={`flex items-end gap-2 p-3 border rounded-lg ${
      isDark 
        ? 'bg-gray-800 border-gray-700' 
        : 'bg-white border-gray-300'
    }`}>
      <textarea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className={`flex-1 resize-none border-none outline-none bg-transparent ${
          isDark ? 'text-white placeholder-gray-400' : 'text-gray-900 placeholder-gray-500'
        }`}
        style={{ minHeight: '24px', maxHeight: '120px' }}
      />
      
      <button
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        className={`p-2 rounded-md transition-colors ${
          disabled || !value.trim()
            ? isDark
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : 'bg-blue-500 hover:bg-blue-600 text-white'
        }`}
        title="Send message (Enter)"
      >
        <PaperAirplaneIcon className="w-5 h-5" />
      </button>
    </div>
  );
};

export default MessageInput;
