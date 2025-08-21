import React, { useEffect } from 'react';
import DocumentList from './DocumentListSimple';
import { documentService, Document } from '../../services/documentService';

interface DocumentStats {
  totalDocs: number;
  processedDocs: number;
  totalSize: number;
  aiAnalyzed: number;
}

interface DocumentManagerWithStatsProps {
  onStatsUpdate?: (stats: DocumentStats) => void;
  className?: string;
}

const DocumentManagerWithStats: React.FC<DocumentManagerWithStatsProps> = ({ 
  onStatsUpdate, 
  className = '' 
}) => {
  // Note: documents and loading state are managed internally by the component

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const result = await documentService.getDocuments(1, 100); // Get more docs for stats
      updateStats(result.documents);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const updateStats = (docs: Document[]) => {
    const stats: DocumentStats = {
      totalDocs: docs.length,
      processedDocs: docs.filter(d => d.status === 'processing').length,
      totalSize: docs.reduce((sum, d) => sum + (d.file_size || 0), 0),
      aiAnalyzed: docs.filter(d => d.summary || d.extracted_text).length
    };
    
    onStatsUpdate?.(stats);
  };

  const handleDocumentUpdate = () => {
    // Reload documents when there are updates
    loadDocuments();
  };

  return (
    <div className={className}>
      <DocumentList 
        onDocumentUpdate={handleDocumentUpdate}
        className="h-full"
      />
    </div>
  );
};

export default DocumentManagerWithStats;
