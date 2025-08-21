import React, { useState } from 'react';
import { 
  FileText, 
  Upload, 
  Brain, 
  Search,
  Filter,
  BarChart3,
  Settings,
  Sparkles
} from 'lucide-react';
import DocumentManagerWithStats from '../components/DocumentManager/DocumentManagerWithStats';

const DocumentsPage: React.FC = () => {
  const [stats, setStats] = useState({
    totalDocs: 0,
    processedDocs: 0,
    totalSize: 0,
    aiAnalyzed: 0
  });

  const handleStatsUpdate = (newStats: typeof stats) => {
    setStats(newStats);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  Documents
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Manage and analyze your documents with AI
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-3 py-1 rounded-full text-sm font-medium flex items-center space-x-1">
              <Sparkles className="w-3 h-3" />
              <span>AI Powered</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="px-6 py-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Documents</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.totalDocs}</p>
              </div>
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">AI Analyzed</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.aiAnalyzed}</p>
              </div>
              <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Size</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{formatFileSize(stats.totalSize)}</p>
              </div>
              <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Processing</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.processedDocs}</p>
              </div>
              <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center">
                <Settings className="w-5 h-5 text-orange-600 dark:text-orange-400 animate-spin" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 px-6 pb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 h-full">
          <DocumentManagerWithStats onStatsUpdate={handleStatsUpdate} />
        </div>
      </div>

      {/* Quick Features Panel */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-6 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-2">
              <Upload className="w-4 h-4" />
              <span>Drag & Drop Upload</span>
            </div>
            <div className="flex items-center space-x-2">
              <Brain className="w-4 h-4" />
              <span>AI Analysis</span>
            </div>
            <div className="flex items-center space-x-2">
              <Search className="w-4 h-4" />
              <span>Smart Search</span>
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4" />
              <span>Advanced Filters</span>
            </div>
          </div>

          <div className="text-xs text-gray-400 dark:text-gray-500">
            Supports PDF, DOCX, PPT, LaTeX, Images, Videos & More
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentsPage;
