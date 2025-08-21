import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  FileText, 
  Image, 
  Video, 
  Music, 
  X, 
  CheckCircle, 
  AlertCircle,
  Loader2
} from 'lucide-react';
import { documentService, Document } from '../../services/documentService';

interface FileWithProgress extends File {
  id: string;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  error?: string;
  document?: Document;
}

interface DocumentUploadProps {
  onUploadComplete?: (documents: Document[]) => void;
  onUploadStart?: () => void;
  maxFiles?: number;
  aiProvider?: string;
  apiKey?: string;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadComplete,
  onUploadStart,
  maxFiles = 10,
  aiProvider,
  apiKey
}) => {
  const [files, setFiles] = useState<FileWithProgress[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: FileWithProgress[] = acceptedFiles.map(file => {
      // Augment the File object with progress properties instead of spreading
      return Object.assign(file, {
        id: Math.random().toString(36).substr(2, 9),
        progress: 0,
        status: 'pending' as const,
        error: undefined as (string | undefined),
      });
    });

    setFiles(prev => [...prev, ...newFiles].slice(0, maxFiles));
  }, [maxFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff'],
      'video/*': ['.mp4', '.mpeg', '.mov', '.avi', '.webm'],
      'audio/*': ['.wav', '.mp3', '.aac', '.ogg', '.flac'],
      'application/x-latex': ['.tex'],
      'text/x-latex': ['.tex']
    },
    maxFiles,
    maxSize: 100 * 1024 * 1024 // 100MB
  });

  const getFileIcon = (file: File) => {
    const fileType = file.type || '';
    if (fileType.startsWith('image/')) return <Image className="w-8 h-8 text-blue-500" />;
    if (fileType.startsWith('video/')) return <Video className="w-8 h-8 text-purple-500" />;
    if (fileType.startsWith('audio/')) return <Music className="w-8 h-8 text-green-500" />;
    return <FileText className="w-8 h-8 text-gray-500" />;
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    onUploadStart?.();

    const uploadPromises = files
      .filter(file => file.status === 'pending')
      .map(async (file) => {
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'uploading' } : f
        ));

        try {
          const document = await documentService.uploadFile(
            file,
            aiProvider,
            apiKey,
            (progress) => {
              setFiles(prev => prev.map(f => 
                f.id === file.id ? { ...f, progress } : f
              ));
            }
          );

          setFiles(prev => prev.map(f => 
            f.id === file.id 
              ? { ...f, status: 'completed', progress: 100, document } 
              : f
          ));

          return document;
        } catch (error) {
          console.error('Upload error:', error);
          const errorMessage = error instanceof Error ? error.message : 'Upload failed';
          setFiles(prev => prev.map(f => 
            f.id === file.id 
              ? { 
                  ...f, 
                  status: 'error', 
                  error: errorMessage
                } 
              : f
          ));
          return null;
        }
      });

    const results = await Promise.all(uploadPromises);
    const successfulUploads = results.filter(doc => doc !== null) as Document[];
    
    setIsUploading(false);
    onUploadComplete?.(successfulUploads);
  };

  const getStatusIcon = (file: FileWithProgress) => {
    switch (file.status) {
      case 'uploading':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  const formatFileSize = (bytes: number | undefined): string => {
    if (!bytes || bytes === 0 || isNaN(bytes)) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500'
          }
        `}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        
        {isDragActive ? (
          <p className="text-lg text-blue-600 dark:text-blue-400">
            Drop the files here...
          </p>
        ) : (
          <div>
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-2">
              Drag & drop files here, or click to select
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Supports PDF, DOCX, PPT, PPTX, LaTeX, RTF, ODT, images, videos, audio files and more
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
              Max file size: 100MB, Max files: {maxFiles}
            </p>
          </div>
        )}
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Files to Upload ({files.length})
          </h3>
          
          <div className="space-y-2">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                {getFileIcon(file)}
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {file.name || 'Unknown file'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {formatFileSize(file.size)} • {file.type || 'Unknown type'}
                  </p>
                  
                  {file.status === 'uploading' && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${file.progress}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {file.progress.toFixed(0)}% uploaded
                      </p>
                    </div>
                  )}
                  
                  {file.status === 'error' && file.error && (
                    <p className="text-xs text-red-500 mt-1">{file.error}</p>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  {getStatusIcon(file)}
                  
                  {file.status !== 'uploading' && (
                    <button
                      onClick={() => removeFile(file.id)}
                      className="text-gray-400 hover:text-red-500 transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Upload Button */}
          <div className="flex justify-end">
            <button
              onClick={uploadFiles}
              disabled={isUploading || files.every(f => f.status !== 'pending')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {isUploading && <Loader2 className="w-4 h-4 animate-spin" />}
              <span>
                {isUploading 
                  ? 'Uploading...' 
                  : `Upload ${files.filter(f => f.status === 'pending').length} Files`
                }
              </span>
            </button>
          </div>
        </div>
      )}

      {/* AI Processing Notice */}
      {(aiProvider && apiKey) && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-5 h-5 text-blue-500 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100">
                AI Analysis Enabled
              </h4>
              <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                Documents will be automatically analyzed with {aiProvider.toUpperCase()} for content extraction and summarization.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;