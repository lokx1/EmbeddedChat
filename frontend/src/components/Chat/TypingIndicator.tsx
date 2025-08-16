/**
 * Modern Typing Indicator Component
 * Shows animated dots when AI is generating response
 */

interface TypingIndicatorProps {
  className?: string;
}

export default function TypingIndicator({ className = '' }: TypingIndicatorProps) {
  return (
    <div className={`flex items-center space-x-1 ${className}`}>
      <span className="text-sm text-gray-500 dark:text-gray-400 mr-2">AI is thinking</span>
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"></div>
      </div>
    </div>
  );
}