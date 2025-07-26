import React from 'react';

interface DocumentViewerProps {
  documentId?: number;
  filename?: string;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({ filename }) => {
  return (
    <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
      <h3 className="text-white text-lg font-medium mb-2">Document Viewer</h3>
      {filename ? (
        <p className="text-gray-400">Viewing: {filename}</p>
      ) : (
        <p className="text-gray-400">Document viewer functionality coming soon...</p>
      )}
    </div>
  );
};
