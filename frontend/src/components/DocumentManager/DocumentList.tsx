import React, { useState, useEffect } from 'react';
import { DocumentCard } from './DocumentCard';
import { Button } from '../UI/Button';
import { Input } from '../UI/Input';
import { Loader } from '../UI/Loader';

export interface Document {
  id: number;
  filename: string;
  originalFilename: string;
  size: number;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  uploadedAt: string;
  summary?: string;
  chunkCount?: number;
  mimeType: string;
}

interface DocumentListProps {
  documents: Document[];
  loading?: boolean;
  onUpload?: () => void;
  onDelete?: (id: number) => void;
  onView?: (document: Document) => void;
  onSearch?: (query: string) => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  loading = false,
  onUpload,
  onDelete,
  onView,
  onSearch
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>(documents);
  const [selectedCategory, setSelectedCategory] = useState('All Categories');

  useEffect(() => {
    let filtered = documents;

    // Filter by search query
    if (searchQuery.trim()) {
      filtered = filtered.filter(doc => 
        doc.originalFilename.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.summary?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by category (based on file type)
    if (selectedCategory !== 'All Categories') {
      filtered = filtered.filter(doc => {
        const category = getDocumentCategory(doc.mimeType);
        return category === selectedCategory;
      });
    }

    setFilteredDocuments(filtered);
  }, [documents, searchQuery, selectedCategory]);

  const getDocumentCategory = (mimeType: string): string => {
    if (mimeType.includes('pdf')) return 'PDF';
    if (mimeType.includes('word') || mimeType.includes('document')) return 'Documents';
    if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) return 'Spreadsheets';
    if (mimeType.includes('text')) return 'Text';
    return 'Other';
  };

  const getDocumentStats = () => {
    const totalSize = documents.reduce((acc, doc) => acc + doc.size, 0);
    const sizeInGB = (totalSize / (1024 * 1024 * 1024)).toFixed(2);
    const indexedCount = documents.filter(doc => doc.status === 'ready').length;
    const categories = [...new Set(documents.map(doc => getDocumentCategory(doc.mimeType)))].length;

    return {
      total: documents.length,
      storageUsed: `${sizeInGB} GB`,
      indexed: indexedCount,
      categories
    };
  };

  const stats = getDocumentStats();

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    onSearch?.(query);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="flex-shrink-0 p-6 border-b border-gray-700">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">Manage Documents</h1>
            <p className="text-gray-400">Organize and manage your document library</p>
          </div>
          <Button 
            onClick={onUpload}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            Upload New
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Documents</p>
                <p className="text-2xl font-bold text-white">{stats.total}</p>
              </div>
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Storage Used</p>
                <p className="text-2xl font-bold text-white">{stats.storageUsed}</p>
              </div>
              <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Indexed</p>
                <p className="text-2xl font-bold text-white">{stats.indexed}</p>
              </div>
              <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Categories</p>
                <p className="text-2xl font-bold text-white">{stats.categories}</p>
              </div>
              <div className="w-10 h-10 bg-yellow-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={handleSearch}
              className="w-full bg-gray-800 border-gray-700 text-white placeholder-gray-400"
            />
          </div>
          <div className="sm:w-48">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="All Categories">All Categories</option>
              <option value="PDF">PDF</option>
              <option value="Documents">Documents</option>
              <option value="Spreadsheets">Spreadsheets</option>
              <option value="Text">Text</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>
      </div>

      {/* Document List - Scrollable content area */}
      <div className="flex-1 min-h-0 overflow-y-auto">
        <div className="p-6">
          {filteredDocuments.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="text-gray-400 text-lg mb-2">
                {searchQuery ? 'No documents found' : 'No documents uploaded yet'}
              </p>
              <p className="text-gray-500">
                {searchQuery ? 'Try adjusting your search criteria' : 'Upload your first document to get started'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredDocuments.map((document) => (
                <DocumentCard
                  key={document.id}
                  document={document}
                  onDelete={() => onDelete?.(document.id)}
                  onView={() => onView?.(document)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
