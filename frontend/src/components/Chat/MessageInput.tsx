/**
 * Modern Message Input Component
 * Design inspired by ChatGPT and Claude input areas
 */
import { useState, useRef, useEffect } from 'react';

interface MessageInputProps {
  onSendMessage: (message: string, files?: File[]) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

export default function MessageInput({ 
  onSendMessage, 
  disabled = false, 
  placeholder = "Type your message...",
  className = '' 
}: MessageInputProps) {
  const [message, setMessage] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const scrollHeight = textarea.scrollHeight;
      const maxHeight = 200; // Maximum height in pixels
      textarea.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
    }
  }, [message]);

  // Handle send message
  const handleSend = () => {
    if (!message.trim() && files.length === 0) return;
    if (disabled) return;

    onSendMessage(message.trim(), files.length > 0 ? files : undefined);
    setMessage('');
    setFiles([]);
    
    // Reset file input to allow re-selecting same files
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Handle file selection
  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return;
    
    const newFiles = Array.from(selectedFiles).slice(0, 5); // Limit to 5 files
    setFiles(prev => [...prev, ...newFiles].slice(0, 5));
    
    // Reset file input to allow re-selecting same files
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Handle file drop
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  // Remove file
  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const canSend = (message.trim() || files.length > 0) && !disabled;

  return (
    <div className={`p-4 ${className}`}>
      {/* File Attachments */}
      {files.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {files.map((file, index) => (
            <div 
              key={index}
              className="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded-lg text-sm"
            >
              <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              <span className="text-gray-700 dark:text-gray-300">{file.name}</span>
              <span className="text-gray-500 text-xs">({formatFileSize(file.size)})</span>
              <button
                onClick={() => removeFile(index)}
                className="text-gray-400 hover:text-red-500 ml-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div 
        className={`relative flex items-end gap-2 p-3 bg-white dark:bg-gray-800 rounded-2xl border shadow-lg transition-all duration-200 ${
          isDragging 
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/10' 
            : 'border-gray-200 dark:border-gray-600'
        } ${disabled ? 'opacity-50' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        {/* File Upload Button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className={`flex-shrink-0 p-2 rounded-lg transition-colors ${
            files.length > 0 
              ? 'text-blue-500 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
          }`}
          title={files.length > 0 ? `${files.length} file(s) selected` : "Attach files"}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        </button>

        {/* Text Input */}
        <div className="flex-1 min-w-0">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={disabled}
            placeholder={isDragging ? "Drop files here..." : placeholder}
            className="w-full resize-none bg-transparent border-none outline-none text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 text-sm leading-6 max-h-[200px]"
            rows={1}
          />
        </div>

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={!canSend}
          className={`flex-shrink-0 p-2 rounded-lg transition-all duration-200 ${
            canSend
              ? 'bg-blue-500 hover:bg-blue-600 text-white shadow-md hover:shadow-lg'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
          }`}
          title="Send message (Enter)"
        >
          {disabled ? (
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,text/*,.pdf,.doc,.docx,video/*,audio/*,.mp4,.mp3,.wav,.avi,.mov,.webm"
          onChange={(e) => handleFileSelect(e.target.files)}
          className="hidden"
        />

        {/* Drag Overlay */}
        {isDragging && (
          <div className="absolute inset-0 bg-blue-50 dark:bg-blue-900/20 border-2 border-dashed border-blue-400 rounded-2xl flex items-center justify-center">
            <div className="text-blue-600 dark:text-blue-400 text-center">
              <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="text-sm font-medium">Drop files here</p>
            </div>
          </div>
        )}
      </div>

      {/* Input Help Text */}
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
        Press <kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">Enter</kbd> to send, 
        <kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs ml-1">Shift + Enter</kbd> for new line
      </div>
    </div>
  );
}