import React, { useState } from 'react';
import { 
  FileText, 
  Image, 
  Video, 
  Music, 
  Download, 
  Eye, 
  Trash2, 
  MoreVertical,
  Calendar,
  HardDrive,
  Brain,
  CheckCircle,
  AlertCircle,
  Clock,
  Loader2
} from 'lucide-react';
import { Document } from '../../services/documentService';

interface DocumentCardProps {
  document: Document;
  onView?: (document: Document) => void;
  onDownload?: (document: Document) => void;
  onDelete?: (document: Document) => void;
  onAnalyze?: (document: Document) => void;
  className?: string;
}

const DocumentCard: React.FC<DocumentCardProps> = ({
  document,
  onView,
  onDownload,
  onDelete,
  onAnalyze,
  className = ''
}) => {
  const [showMenu, setShowMenu] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const getFileIcon = () => {
    if (document.mime_type?.startsWith('image/')) {
      return <Image className="w-8 h-8 text-blue-500" />;
    }
    if (document.mime_type?.startsWith('video/')) {
      return <Video className="w-8 h-8 text-purple-500" />;
    }
    if (document.mime_type?.startsWith('audio/')) {
      return <Music className="w-8 h-8 text-green-500" />;
    }
    return <FileText className="w-8 h-8 text-gray-500" />;
  };

  const getFileExtension = () => {
    const filename = document.original_filename || document.filename;
    return filename.split('.').pop()?.toLowerCase() || '';
  };

  const getStatusColor = () => {
    switch (document.status) {
      case 'ready':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20 dark:text-green-400';
      case 'processing':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'error':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20 dark:text-red-400';
      case 'uploading':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20 dark:text-blue-400';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const getStatusIcon = () => {
    switch (document.status) {
      case 'ready':
        return <CheckCircle className="w-4 h-4" />;
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-4 h-4" />;
      case 'uploading':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleAnalyze = async () => {
    if (onAnalyze) {
      setIsAnalyzing(true);
      try {
        await onAnalyze(document);
      } finally {
        setIsAnalyzing(false);
      }
    }
  };

  const getThumbnail = () => {
    if (document.mime_type?.startsWith('image/')) {
      return (
        <div className="w-full h-32 bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden mb-3">
          <img
            src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/documents/${document.id}/download`}
            alt={document.original_filename || document.filename}
            className="w-full h-full object-cover"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
            }}
          />
        </div>
      );
    }

    return (
      <div className="w-full h-32 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 rounded-lg flex items-center justify-center mb-3">
        {getFileIcon()}
      </div>
    );
  };

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all duration-200 ${className}`}>
      {/* Thumbnail */}
      {getThumbnail()}

      {/* Content */}
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 truncate">
              {document.original_filename || document.filename}
            </h3>
            <div className="flex items-center space-x-2 mt-1">
              <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded">
                {getFileExtension().toUpperCase()}
              </span>
              <span className={`px-2 py-1 text-xs rounded flex items-center space-x-1 ${getStatusColor()}`}>
                {getStatusIcon()}
                <span className="capitalize">{document.status}</span>
              </span>
            </div>
          </div>

          {/* Menu */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"
            >
              <MoreVertical className="w-4 h-4 text-gray-400" />
            </button>

            {showMenu && (
              <div className="absolute right-0 top-8 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-10">
                <div className="py-1">
                  {onView && (
                    <button
                      onClick={() => {
                        onView(document);
                        setShowMenu(false);
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                    >
                      <Eye className="w-4 h-4" />
                      <span>View</span>
                    </button>
                  )}
                  
                  {onDownload && (
                    <button
                      onClick={() => {
                        onDownload(document);
                        setShowMenu(false);
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download</span>
                    </button>
                  )}

                  {onAnalyze && document.status === 'ready' && (
                    <button
                      onClick={() => {
                        handleAnalyze();
                        setShowMenu(false);
                      }}
                      disabled={isAnalyzing}
                      className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2 disabled:opacity-50"
                    >
                      {isAnalyzing ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Brain className="w-4 h-4" />
                      )}
                      <span>{isAnalyzing ? 'Analyzing...' : 'Analyze with AI'}</span>
                    </button>
                  )}

                  {onDelete && (
                    <button
                      onClick={() => {
                        onDelete(document);
                        setShowMenu(false);
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center space-x-2"
                    >
                      <Trash2 className="w-4 h-4" />
                      <span>Delete</span>
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Metadata */}
        <div className="space-y-2 text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center space-x-1">
            <HardDrive className="w-3 h-3" />
            <span>{formatFileSize(document.file_size)}</span>
          </div>
          
          <div className="flex items-center space-x-1">
            <Calendar className="w-3 h-3" />
            <span>{formatDate(document.created_at)}</span>
          </div>
        </div>

        {/* Summary Preview */}
        {document.summary && (
          <div className="mt-3 p-2 bg-blue-50 dark:bg-blue-900/20 rounded border-l-2 border-blue-200 dark:border-blue-800">
            <p className="text-xs text-blue-700 dark:text-blue-300 leading-relaxed line-clamp-3">
              {document.summary}
            </p>
          </div>
        )}

        {/* Error Message */}
        {document.status === 'error' && document.error_message && (
          <div className="mt-3 p-2 bg-red-50 dark:bg-red-900/20 rounded border-l-2 border-red-200 dark:border-red-800">
            <p className="text-xs text-red-700 dark:text-red-300">
              {document.error_message}
            </p>
          </div>
        )}

        {/* Quick Actions */}
        <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            {onView && (
              <button
                onClick={() => onView(document)}
                className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium flex items-center space-x-1"
              >
                <Eye className="w-3 h-3" />
                <span>View</span>
              </button>
            )}
            
            {onDownload && (
              <button
                onClick={() => onDownload(document)}
                className="text-xs text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 font-medium flex items-center space-x-1"
              >
                <Download className="w-3 h-3" />
                <span>Download</span>
              </button>
            )}
          </div>

          {document.extracted_text && (
            <div className="flex items-center space-x-1 text-xs text-green-600 dark:text-green-400">
              <Brain className="w-3 h-3" />
              <span>AI Processed</span>
            </div>
          )}
        </div>
      </div>

      {/* Click outside to close menu */}
      {showMenu && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setShowMenu(false)}
        />
      )}
    </div>
  );
};

export default DocumentCard;