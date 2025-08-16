/**
 * File Upload Component for Chat
 */
import React, { useRef, useState, useCallback } from 'react';
import { 
  CloudArrowUpIcon, 
  DocumentIcon, 
  PhotoIcon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { documentService, Document } from '../../services/documentService';
import { AIProvider } from './types';

interface FileUploadProps {
  onFileUploaded?: (document: Document) => void;
  onFileProcessed?: (document: Document, analysis: string) => void;
  aiProvider?: AIProvider;
  apiKey?: string;
  maxFileSize?: number; // in bytes
  className?: string;
}

interface UploadingFile {
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
  document?: Document;
  analysis?: string;
}

export default function FileUpload({
  onFileUploaded,
  onFileProcessed,
  aiProvider,
  apiKey,
  maxFileSize = 50 * 1024 * 1024, // 50MB
  className = ''
}: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);

  const handleFiles = useCallback(async (files: FileList) => {
    const fileArray = Array.from(files);
    
    // Validate files
    const validFiles = fileArray.filter(file => {
      if (!documentService.isSupportedFileType(file)) {
        alert(`File type ${file.type || 'unknown'} is not supported`);
        return false;
      }
      
      if (file.size > maxFileSize) {
        alert(`File ${file.name} is too large. Maximum size is ${documentService.formatFileSize(maxFileSize)}`);
        return false;
      }
      
      return true;
    });

    if (validFiles.length === 0) return;

    // Add files to uploading state
    const newUploadingFiles: UploadingFile[] = validFiles.map(file => ({
      file,
      progress: 0,
      status: 'uploading'
    }));

    setUploadingFiles(prev => [...prev, ...newUploadingFiles]);

    // Upload files
    for (let i = 0; i < validFiles.length; i++) {
      const file = validFiles[i];
      const fileIndex = uploadingFiles.length + i;

      try {
        // Upload with progress tracking
        const document = await documentService.uploadFile(
          file,
          aiProvider,
          apiKey,
          (progress) => {
            setUploadingFiles(prev => 
              prev.map((uploadFile, index) => 
                index === fileIndex 
                  ? { ...uploadFile, progress }
                  : uploadFile
              )
            );
          }
        );

        // Update status
        setUploadingFiles(prev => 
          prev.map((uploadFile, index) => 
            index === fileIndex 
              ? { 
                  ...uploadFile, 
                  status: document.status === 'processing' ? 'processing' : 'completed',
                  document,
                  progress: 100
                }
              : uploadFile
          )
        );

        // Callback
        if (onFileUploaded) {
          onFileUploaded(document);
        }

        // If document is processed and has analysis, call processed callback
        if (document.status === 'ready' && document.summary && onFileProcessed) {
          onFileProcessed(document, document.summary);
        }

      } catch (error) {
        console.error('Upload error:', error);
        
        setUploadingFiles(prev => 
          prev.map((uploadFile, index) => 
            index === fileIndex 
              ? { 
                  ...uploadFile, 
                  status: 'error',
                  error: error instanceof Error ? error.message : 'Upload failed'
                }
              : uploadFile
          )
        );
      }
    }
  }, [aiProvider, apiKey, maxFileSize, onFileUploaded, onFileProcessed, uploadingFiles.length]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  }, [handleFiles]);

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const removeUploadingFile = (index: number) => {
    setUploadingFiles(prev => prev.filter((_, i) => i !== index));
  };

  const getFileIcon = (file: File) => {
    const category = documentService.getFileCategory(file.type);
    
    switch (category) {
      case 'image':
        return <PhotoIcon className="w-5 h-5 text-blue-500" />;
      case 'document':
      case 'data':
        return <DocumentIcon className="w-5 h-5 text-green-500" />;
      default:
        return <DocumentIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusIcon = (status: UploadingFile['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <ArrowPathIcon className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircleIcon className="w-4 h-4 text-green-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Drop Zone */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-6 text-center transition-colors
          ${dragActive 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
          }
          ${uploadingFiles.length > 0 ? 'mb-4' : ''}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleInputChange}
          accept=".pdf,.doc,.docx,.txt,.md,.csv,.json,.jpg,.jpeg,.png,.gif,.webp,.bmp,.tiff,.xls,.xlsx"
          className="hidden"
        />
        
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
        <div className="mt-4">
          <button
            type="button"
            onClick={openFileDialog}
            className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
          >
            Click to upload
          </button>
          <span className="text-gray-500 dark:text-gray-400"> or drag and drop</span>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          PDF, Word, Images, CSV, JSON up to {documentService.formatFileSize(maxFileSize)}
        </p>
        
        {aiProvider && apiKey && (
          <div className="mt-3 text-xs text-blue-600 dark:text-blue-400">
            🤖 AI analysis with {aiProvider.toUpperCase()} enabled
          </div>
        )}
      </div>

      {/* Uploading Files */}
      {uploadingFiles.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
            Uploading Files ({uploadingFiles.length})
          </h4>
          
          {uploadingFiles.map((uploadFile, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800"
            >
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                {getFileIcon(uploadFile.file)}
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {uploadFile.file.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {documentService.formatFileSize(uploadFile.file.size)}
                  </p>
                  
                  {/* Progress bar */}
                  {(uploadFile.status === 'uploading' || uploadFile.status === 'processing') && (
                    <div className="mt-1">
                      <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-1">
                        <div
                          className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                          style={{ width: `${uploadFile.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Status text */}
                  <p className="text-xs mt-1">
                    {uploadFile.status === 'uploading' && (
                      <span className="text-blue-600">Uploading... {Math.round(uploadFile.progress)}%</span>
                    )}
                    {uploadFile.status === 'processing' && (
                      <span className="text-blue-600">Processing with AI...</span>
                    )}
                    {uploadFile.status === 'completed' && (
                      <span className="text-green-600">
                        {uploadFile.document?.summary ? 'Processed with AI' : 'Uploaded successfully'}
                      </span>
                    )}
                    {uploadFile.status === 'error' && (
                      <span className="text-red-600">{uploadFile.error}</span>
                    )}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {getStatusIcon(uploadFile.status)}
                
                <button
                  onClick={() => removeUploadingFile(index)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <XMarkIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}