/**
 * Document Viewer Component for Chat
 */
import React, { useState } from 'react';
import {
  DocumentIcon,
  PhotoIcon,
  ChartBarIcon,
  EyeIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  SparklesIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { Document, documentService } from '../../services/documentService';
import { AIProvider } from './types';

interface DocumentViewerProps {
  documents: Document[];
  onDocumentSelect?: (document: Document) => void;
  onDocumentDelete?: (documentId: number) => void;
  onDocumentAnalyze?: (document: Document, analysis: string) => void;
  aiProvider?: AIProvider;
  apiKey?: string;
  className?: string;
}

interface DocumentDetailsModalProps {
  document: Document;
  onClose: () => void;
  onAnalyze?: (analysis: string) => void;
  aiProvider?: AIProvider;
  apiKey?: string;
}

function DocumentDetailsModal({ 
  document, 
  onClose, 
  onAnalyze,
  aiProvider,
  apiKey 
}: DocumentDetailsModalProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [content, setContent] = useState<string>('');
  const [loadingContent, setLoadingContent] = useState(false);

  const loadContent = async () => {
    setLoadingContent(true);
    try {
      const contentData = await documentService.getDocumentContent(document.id);
      setContent(contentData.content);
    } catch (error) {
      console.error('Error loading content:', error);
      setContent('Error loading content');
    } finally {
      setLoadingContent(false);
    }
  };

  const handleAnalyze = async () => {
    if (!aiProvider || !apiKey) {
      alert('AI provider and API key are required for analysis');
      return;
    }

    setIsAnalyzing(true);
    try {
      const result = await documentService.analyzeDocument(document.id, aiProvider, apiKey);
      if (result.success && onAnalyze) {
        onAnalyze(result.analysis);
      } else {
        alert(`Analysis failed: ${result.message}`);
      }
    } catch (error) {
      console.error('Analysis error:', error);
      alert(`Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  React.useEffect(() => {
    if (!document.extracted_text) {
      loadContent();
    } else {
      setContent(document.extracted_text);
    }
  }, [document]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            {documentService.getFileCategory(document.mime_type) === 'image' ? (
              <PhotoIcon className="w-6 h-6 text-blue-500" />
            ) : (
              <DocumentIcon className="w-6 h-6 text-green-500" />
            )}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {document.original_filename}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {documentService.formatFileSize(document.file_size)} • {document.mime_type}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {aiProvider && apiKey && (
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAnalyzing ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <SparklesIcon className="w-4 h-4" />
                )}
                <span>{isAnalyzing ? 'Analyzing...' : 'Analyze with AI'}</span>
              </button>
            )}
            
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 max-h-[70vh] overflow-y-auto">
          {/* Status */}
          <div className="mb-4">
            <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${
              document.status === 'ready' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
              document.status === 'processing' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
              document.status === 'error' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
              'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
            }`}>
              {document.status}
            </span>
          </div>

          {/* Summary */}
          {document.summary && (
            <div className="mb-6">
              <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                AI Summary
              </h4>
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm text-gray-700 dark:text-gray-300">{document.summary}</p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {document.error_message && (
            <div className="mb-6">
              <h4 className="text-sm font-medium text-red-900 dark:text-red-100 mb-2">
                Error
              </h4>
              <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <p className="text-sm text-red-700 dark:text-red-300">{document.error_message}</p>
              </div>
            </div>
          )}

          {/* Content */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
              Extracted Content
            </h4>
            
            {loadingContent ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <span className="ml-2 text-gray-600 dark:text-gray-400">Loading content...</span>
              </div>
            ) : (
              <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg max-h-96 overflow-y-auto">
                <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-mono">
                  {content || 'No content available'}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DocumentViewer({
  documents,
  onDocumentSelect,
  onDocumentDelete,
  onDocumentAnalyze,
  aiProvider,
  apiKey,
  className = ''
}: DocumentViewerProps) {
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);

  const getFileIcon = (mimeType: string) => {
    const category = documentService.getFileCategory(mimeType);
    
    switch (category) {
      case 'image':
        return <PhotoIcon className="w-5 h-5 text-blue-500" />;
      case 'data':
        return <ChartBarIcon className="w-5 h-5 text-purple-500" />;
      case 'document':
        return <DocumentIcon className="w-5 h-5 text-green-500" />;
      default:
        return <DocumentIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const handleViewDocument = (document: Document) => {
    setSelectedDocument(document);
  };

  const handleAnalyzeFromModal = (analysis: string) => {
    if (selectedDocument && onDocumentAnalyze) {
      onDocumentAnalyze(selectedDocument, analysis);
    }
    setSelectedDocument(null);
  };

  const handleDeleteDocument = async (documentId: number, event: React.MouseEvent) => {
    event.stopPropagation();
    
    if (confirm('Are you sure you want to delete this document?')) {
      try {
        await documentService.deleteDocument(documentId);
        if (onDocumentDelete) {
          onDocumentDelete(documentId);
        }
      } catch (error) {
        console.error('Delete error:', error);
        alert(`Failed to delete document: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }
  };

  if (documents.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 dark:text-gray-400 ${className}`}>
        <DocumentIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p>No documents uploaded yet</p>
      </div>
    );
  }

  return (
    <>
      <div className={`space-y-2 ${className}`}>
        <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
          Documents ({documents.length})
        </h4>
        
        {documents.map((document) => (
          <div
            key={document.id}
            className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer group"
            onClick={() => onDocumentSelect?.(document)}
          >
            <div className="flex items-center space-x-3 flex-1 min-w-0">
              {getFileIcon(document.mime_type)}
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {document.original_filename}
                </p>
                <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                  <span>{documentService.formatFileSize(document.file_size)}</span>
                  <span>•</span>
                  <span className={`${
                    document.status === 'ready' ? 'text-green-600 dark:text-green-400' :
                    document.status === 'processing' ? 'text-blue-600 dark:text-blue-400' :
                    document.status === 'error' ? 'text-red-600 dark:text-red-400' :
                    'text-gray-600 dark:text-gray-400'
                  }`}>
                    {document.status}
                  </span>
                  {document.summary && (
                    <>
                      <span>•</span>
                      <span className="text-blue-600 dark:text-blue-400">AI analyzed</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleViewDocument(document);
                }}
                className="p-1 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
                title="View document"
              >
                <EyeIcon className="w-4 h-4" />
              </button>
              
              <button
                onClick={(e) => handleDeleteDocument(document.id, e)}
                className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                title="Delete document"
              >
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Document Details Modal */}
      {selectedDocument && (
        <DocumentDetailsModal
          document={selectedDocument}
          onClose={() => setSelectedDocument(null)}
          onAnalyze={handleAnalyzeFromModal}
          aiProvider={aiProvider}
          apiKey={apiKey}
        />
      )}
    </>
  );
}
