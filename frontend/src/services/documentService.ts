/**
 * Document service for file upload and management
 */

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  error_message?: string;
  extracted_text?: string;
  summary?: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentList {
  documents: Document[];
  total: number;
  page: number;
  size: number;
}

export interface UploadResponse extends Document {}

export interface AnalysisResponse {
  success: boolean;
  document: Document;
  analysis: string;
  message: string;
}

export interface DocumentContent {
  document_id: number;
  filename: string;
  content: string;
  summary?: string;
  status: string;
}

class DocumentService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Upload a file and optionally process it with AI
   */
  async uploadFile(
    file: File,
    aiProvider?: string,
    apiKey?: string,
    onProgress?: (progress: number) => void
  ): Promise<UploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      if (aiProvider) {
        formData.append('ai_provider', aiProvider);
      }
      
      if (apiKey) {
        formData.append('api_key', apiKey);
      }

      const xhr = new XMLHttpRequest();
      
      return new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable && onProgress) {
            const progress = (e.loaded / e.total) * 100;
            onProgress(progress);
          }
        });

        xhr.addEventListener('load', () => {
          if (xhr.status === 201) {
            try {
              const response = JSON.parse(xhr.responseText);
              resolve(response);
            } catch (e) {
              reject(new Error('Invalid response format'));
            }
          } else {
            try {
              const error = JSON.parse(xhr.responseText);
              reject(new Error(error.detail || `Upload failed: ${xhr.status}`));
            } catch (e) {
              reject(new Error(`Upload failed: ${xhr.status}`));
            }
          }
        });

        xhr.addEventListener('error', () => {
          reject(new Error('Network error during upload'));
        });

        xhr.open('POST', `${this.baseUrl}/api/v1/documents/upload`);
        xhr.send(formData);
      });

    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  /**
   * Get list of user documents
   */
  async getDocuments(
    page: number = 1,
    limit: number = 20,
    status?: string
  ): Promise<DocumentList> {
    try {
      const params = new URLSearchParams({
        skip: ((page - 1) * limit).toString(),
        limit: limit.toString()
      });

      if (status) {
        params.append('status', status);
      }

      const response = await fetch(`${this.baseUrl}/api/v1/documents/?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Get documents error:', error);
      throw error;
    }
  }

  /**
   * Get a specific document
   */
  async getDocument(documentId: number): Promise<Document> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/documents/${documentId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Get document error:', error);
      throw error;
    }
  }

  /**
   * Analyze a document with AI
   */
  async analyzeDocument(
    documentId: number,
    aiProvider: string,
    apiKey: string
  ): Promise<AnalysisResponse> {
    try {
      const formData = new FormData();
      formData.append('ai_provider', aiProvider);
      formData.append('api_key', apiKey);

      const response = await fetch(`${this.baseUrl}/api/v1/documents/${documentId}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Analyze document error:', error);
      throw error;
    }
  }

  /**
   * Get document content
   */
  async getDocumentContent(documentId: number): Promise<DocumentContent> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/documents/${documentId}/content`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Get document content error:', error);
      throw error;
    }
  }

  /**
   * Delete a document
   */
  async deleteDocument(documentId: number): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/documents/${documentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      console.error('Delete document error:', error);
      throw error;
    }
  }

  /**
   * Check if file type is supported
   */
  isSupportedFileType(file: File): boolean {
    const supportedTypes = [
      // Text documents
      'text/plain',
      'text/markdown',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/csv',
      'application/json',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      
      // PowerPoint formats
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      
      // LaTeX formats
      'application/x-latex',
      'text/x-latex',
      'application/x-tex',
      'text/x-tex',
      
      // Rich text formats
      'application/rtf',
      'text/rtf',
      
      // OpenDocument formats
      'application/vnd.oasis.opendocument.text',
      'application/vnd.oasis.opendocument.presentation',
      'application/vnd.oasis.opendocument.spreadsheet',
      
      // Images (including new formats)
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/gif',
      'image/webp',
      'image/bmp',
      'image/tiff',
      'image/heic',
      'image/heif',
      
      // Video types supported by Gemini
      'video/mp4',
      'video/mpeg',
      'video/mov',
      'video/avi',
      'video/x-flv',
      'video/mpg',
      'video/webm',
      'video/wmv',
      'video/3gpp',
      
      // Audio types supported by Gemini
      'audio/wav',
      'audio/mp3',
      'audio/aiff',
      'audio/aac',
      'audio/ogg',
      'audio/flac'
    ];

    return supportedTypes.includes(file.type);
  }

  /**
   * Get file type category
   */
  getFileCategory(mimeType: string): 'image' | 'document' | 'data' | 'unknown' {
    if (mimeType.startsWith('image/')) {
      return 'image';
    }
    
    const documentTypes = [
      'text/plain',
      'text/markdown', 
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'application/x-latex',
      'text/x-latex',
      'application/x-tex',
      'text/x-tex',
      'application/rtf',
      'text/rtf',
      'application/vnd.oasis.opendocument.text',
      'application/vnd.oasis.opendocument.presentation'
    ];
    
    const dataTypes = [
      'text/csv',
      'application/json',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    if (documentTypes.includes(mimeType)) {
      return 'document';
    }
    
    if (dataTypes.includes(mimeType)) {
      return 'data';
    }
    
    return 'unknown';
  }

  /**
   * Format file size for display
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}

// Export singleton instance
export const documentService = new DocumentService();
export default documentService;
