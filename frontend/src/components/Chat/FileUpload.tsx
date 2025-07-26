import React, { useRef } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { PaperClipIcon } from '@heroicons/react/24/outline';

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void;
  disabled?: boolean;
  accept?: string;
  multiple?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFilesSelected,
  disabled = false,
  accept = '.txt,.md,.pdf,.doc,.docx,.json,.csv',
  multiple = true,
}) => {
  const { isDark } = useTheme();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      onFilesSelected(files);
    }
    // Reset input to allow selecting the same file again
    e.target.value = '';
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileChange}
        className="hidden"
        disabled={disabled}
      />
      
      <button
        onClick={handleClick}
        disabled={disabled}
        className={`p-2 rounded-md transition-colors ${
          disabled
            ? isDark
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : isDark
              ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
              : 'bg-gray-200 hover:bg-gray-300 text-gray-600'
        }`}
        title="Upload files"
      >
        <PaperClipIcon className="w-5 h-5" />
      </button>
    </>
  );
};
