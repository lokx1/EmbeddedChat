import React from 'react';
import { FileText, Sparkles } from 'lucide-react';
import DocumentList from '../components/DocumentManager/DocumentListSimple';
import ErrorBoundary from '../components/ErrorBoundary/ErrorBoundary';

const SimpleDocumentsPage: React.FC = () => {
  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Simple Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
              <FileText className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Documents
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Upload and manage your files
              </p>
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center space-x-1">
            <Sparkles className="w-3 h-3" />
            <span>AI Powered</span>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 min-h-0">
        <ErrorBoundary>
          <DocumentList className="h-full" />
        </ErrorBoundary>
      </div>
    </div>
  );
};

export default SimpleDocumentsPage;
