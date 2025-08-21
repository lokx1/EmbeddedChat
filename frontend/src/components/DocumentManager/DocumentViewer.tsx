import React, { useState, useEffect, useMemo } from 'react';
import { 
  FileText, 
  Download, 
  ZoomIn, 
  ZoomOut, 
  RotateCw, 
  Eye,
  EyeOff,
  Loader2
} from 'lucide-react';
import { Document as DocumentType } from '../../services/documentService';

interface DocumentViewerProps {
  document: DocumentType;
  className?: string;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ document, className = '' }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  // const [currentPage, setCurrentPage] = useState(1);
  // const [totalPages, setTotalPages] = useState(1);
  const [showPreview, setShowPreview] = useState(true);
  const [viewerContent, setViewerContent] = useState<string | null>(null);

  const fileExtension = useMemo(() => {
    const filename = document.original_filename || document.filename;
    return filename.split('.').pop()?.toLowerCase() || '';
  }, [document]);

  const isImageFile = useMemo(() => {
    return document.mime_type?.startsWith('image/') || false;
  }, [document]);

  const isPDFFile = useMemo(() => {
    return document.mime_type === 'application/pdf' || fileExtension === 'pdf';
  }, [document.mime_type, fileExtension]);

  const isTextFile = useMemo(() => {
    const textTypes = ['text/plain', 'text/markdown', 'application/json'];
    const textExtensions = ['txt', 'md', 'json', 'tex', 'latex'];
    return textTypes.includes(document.mime_type || '') || textExtensions.includes(fileExtension);
  }, [document.mime_type, fileExtension]);

  const isOfficeFile = useMemo(() => {
    const officeTypes = [
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    ];
    const officeExtensions = ['doc', 'docx', 'ppt', 'pptx'];
    return officeTypes.includes(document.mime_type || '') || officeExtensions.includes(fileExtension);
  }, [document.mime_type, fileExtension]);

  useEffect(() => {
    loadDocumentContent();
  }, [document]);

  const loadDocumentContent = async () => {
    setIsLoading(true);
    setError(null);

    try {
      if (isTextFile && document.extracted_text) {
        setViewerContent(document.extracted_text);
        setIsLoading(false);
        return;
      }

      if (isImageFile) {
        // For images, we'll show the file directly
        setViewerContent(document.file_path);
        setIsLoading(false);
        return;
      }

      if (isPDFFile) {
        // For PDFs, we'll use PDF.js (to be implemented)
        setViewerContent('PDF_VIEWER');
        setIsLoading(false);
        return;
      }

      if (isOfficeFile) {
        // For Office files, we'll show extracted text or use office viewer
        if (document.extracted_text) {
          setViewerContent(document.extracted_text);
        } else {
          setViewerContent('OFFICE_VIEWER');
        }
        setIsLoading(false);
        return;
      }

      // Fallback to extracted text
      if (document.extracted_text) {
        setViewerContent(document.extracted_text);
      } else {
        setError('No preview available for this file type');
      }
      setIsLoading(false);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load document');
      setIsLoading(false);
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 25, 300));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 25, 25));
  };

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  const handleDownload = () => {
    // Create download link
    const link = window.document.createElement('a');
    link.href = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/documents/${document.id}/download`;
    link.download = document.original_filename || document.filename;
    window.document.body.appendChild(link);
    link.click();
    window.document.body.removeChild(link);
  };

  const renderTextViewer = () => (
    <div className="w-full h-full overflow-auto">
      <div 
        className="p-6 bg-white dark:bg-gray-900 min-h-full font-mono text-sm leading-relaxed"
        style={{ 
          transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
          transformOrigin: 'top left'
        }}
      >
        <pre className="whitespace-pre-wrap text-gray-800 dark:text-gray-200">
          {viewerContent}
        </pre>
      </div>
    </div>
  );

  const renderImageViewer = () => (
    <div className="w-full h-full flex items-center justify-center overflow-auto bg-gray-100 dark:bg-gray-800">
      <img
        src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/documents/${document.id}/download`}
        alt={document.original_filename || document.filename}
        className="max-w-full max-h-full object-contain"
        style={{ 
          transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
          transformOrigin: 'center'
        }}
        onError={() => setError('Failed to load image')}
      />
    </div>
  );

  const renderPDFViewer = () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-100 dark:bg-gray-800">
      <div className="text-center">
        <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 dark:text-gray-400 mb-2">PDF Viewer</p>
        <p className="text-sm text-gray-500 dark:text-gray-500">
          Advanced PDF viewing will be implemented with PDF.js
        </p>
        {document.extracted_text && (
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 mx-auto"
          >
            {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            <span>{showPreview ? 'Hide Text' : 'Show Extracted Text'}</span>
          </button>
        )}
        {showPreview && document.extracted_text && (
          <div className="mt-4 p-4 bg-white dark:bg-gray-900 rounded-lg text-left max-w-4xl">
            <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200">
              {document.extracted_text}
            </pre>
          </div>
        )}
      </div>
    </div>
  );

  const renderOfficeViewer = () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-100 dark:bg-gray-800">
      <div className="text-center max-w-4xl">
        <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 dark:text-gray-400 mb-2">
          {fileExtension.toUpperCase()} Document
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-500 mb-4">
          {document.original_filename || document.filename}
        </p>
        
        {document.extracted_text ? (
          <div className="p-6 bg-white dark:bg-gray-900 rounded-lg text-left">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Extracted Content
            </h3>
            <div 
              className="prose dark:prose-invert max-w-none"
              style={{ 
                transform: `scale(${zoom / 100})`,
                transformOrigin: 'top left'
              }}
            >
              <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200 leading-relaxed">
                {document.extracted_text}
              </pre>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-500 dark:text-gray-500">
            No extracted content available. Try analyzing this document with AI.
          </p>
        )}
      </div>
    </div>
  );

  const renderViewer = () => {
    if (error) {
      return (
        <div className="w-full h-full flex items-center justify-center">
          <div className="text-center">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        </div>
      );
    }

    if (isTextFile) return renderTextViewer();
    if (isImageFile) return renderImageViewer();
    if (isPDFFile) return renderPDFViewer();
    if (isOfficeFile) return renderOfficeViewer();

    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            Preview not available for this file type
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
            {document.original_filename || document.filename}
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className={`flex flex-col bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 truncate">
            {document.original_filename || document.filename}
          </h3>
          <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded">
            {fileExtension.toUpperCase()}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          {/* Zoom Controls */}
          <div className="flex items-center space-x-1 border border-gray-200 dark:border-gray-700 rounded">
            <button
              onClick={handleZoomOut}
              disabled={zoom <= 25}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="px-2 py-1 text-sm text-gray-600 dark:text-gray-400 min-w-12 text-center">
              {zoom}%
            </span>
            <button
              onClick={handleZoomIn}
              disabled={zoom >= 300}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
          </div>

          {/* Rotate */}
          <button
            onClick={handleRotate}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"
            title="Rotate"
          >
            <RotateCw className="w-4 h-4" />
          </button>

          {/* Download */}
          <button
            onClick={handleDownload}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"
            title="Download"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Viewer Content */}
      <div className="flex-1 relative min-h-96">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-2" />
              <p className="text-gray-600 dark:text-gray-400">Loading document...</p>
            </div>
          </div>
        ) : (
          renderViewer()
        )}
      </div>

      {/* Document Info */}
      {document.summary && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">
            AI Summary
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            {document.summary}
          </p>
        </div>
      )}
    </div>
  );
};

export default DocumentViewer;