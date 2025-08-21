import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Grid, 
  List, 
  RefreshCw,
  Plus,
  FileText
} from 'lucide-react';
import DocumentCard from './DocumentCard';
import DocumentViewer from './DocumentViewer';
import DocumentUpload from './DocumentUpload';
import { Document, DocumentList as DocumentListType, documentService } from '../../services/documentService';

interface DocumentListProps {
  className?: string;
  onDocumentSelect?: (document: Document) => void;
  onDocumentUpdate?: () => void;
}

const DocumentList: React.FC<DocumentListProps> = ({ 
  className = '',
  onDocumentSelect,
  onDocumentUpdate
}) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const result: DocumentListType = await documentService.getDocuments(1, 50);
      setDocuments(result.documents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const filteredDocuments = documents.filter(doc => 
    searchQuery === '' || 
    (doc.original_filename || doc.filename).toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.mime_type?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDocumentView = (document: Document) => {
    setSelectedDocument(document);
    onDocumentSelect?.(document);
  };

  const handleDocumentDownload = (document: Document) => {
    const link = window.document.createElement('a');
    link.href = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/documents/${document.id}/download`;
    link.download = document.original_filename || document.filename;
    window.document.body.appendChild(link);
    link.click();
    window.document.body.removeChild(link);
  };

  const handleDocumentDelete = async (document: Document) => {
    if (!confirm(`Are you sure you want to delete "${document.original_filename || document.filename}"?`)) {
      return;
    }

    try {
      await documentService.deleteDocument(document.id);
      setDocuments(prev => prev.filter(doc => doc.id !== document.id));
      onDocumentUpdate?.();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete document');
    }
  };

  const handleUploadComplete = (newDocuments: Document[]) => {
    setDocuments(prev => [...newDocuments, ...prev]);
    setShowUpload(false);
    onDocumentUpdate?.();
  };

  if (selectedDocument) {
    return (
      <div className="h-full flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setSelectedDocument(null)}
            className="text-blue-600 hover:text-blue-700"
          >
            ← Back to Documents
          </button>
        </div>
        <div className="flex-1 p-4">
          <DocumentViewer document={selectedDocument} className="h-full" />
        </div>
      </div>
    );
  }

  if (showUpload) {
    return (
      <div className="h-full flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold">Upload Documents</h2>
          <button
            onClick={() => setShowUpload(false)}
            className="text-gray-600 hover:text-gray-900"
          >
            Cancel
          </button>
        </div>
        <div className="flex-1 p-4 overflow-auto">
          <DocumentUpload onUploadComplete={handleUploadComplete} />
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Simple Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
        <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          {documents.length} Documents
        </h2>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowUpload(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Upload</span>
          </button>
          
          <button
            onClick={loadDocuments}
            disabled={loading}
            className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Search and View Controls */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-sm"
            />
          </div>
          <div className="flex items-center space-x-1 border border-gray-300 dark:border-gray-600 rounded-lg">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400'}`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 ${viewMode === 'list' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400'}`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Content - Scrollable Area */}
      <div className="flex-1 overflow-auto min-h-0">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <p className="text-red-600 dark:text-red-400 mb-2">{error}</p>
              <button
                onClick={loadDocuments}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Retry
              </button>
            </div>
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                No documents found
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {searchQuery 
                  ? 'Try adjusting your search query' 
                  : 'Upload your first document to get started'
                }
              </p>
              <button
                onClick={() => setShowUpload(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Upload Document
              </button>
            </div>
          </div>
        ) : (
          <div className="p-6">
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-6">
                {filteredDocuments.map(document => (
                  <DocumentCard
                    key={document.id}
                    document={document}
                    onView={handleDocumentView}
                    onDownload={handleDocumentDownload}
                    onDelete={handleDocumentDelete}
                  />
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {filteredDocuments.map(document => (
                  <DocumentCard
                    key={document.id}
                    document={document}
                    onView={handleDocumentView}
                    onDownload={handleDocumentDownload}
                    onDelete={handleDocumentDelete}
                    className="!flex !flex-row !items-center !space-x-4"
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentList;
