# File upload handling service
import os
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from .document_processor import DocumentProcessor
from ...models.document import Document, DocumentStatus

logger = logging.getLogger(__name__)


class UploadService:
    """Service for handling file uploads and processing"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
    
    async def process_uploaded_document(
        self,
        document: Document,
        ai_provider: str = None,
        api_key: str = None
    ) -> Dict[str, Any]:
        """
        Process uploaded document and extract content/analysis
        
        Args:
            document: Document model instance
            ai_provider: AI provider for analysis (optional)
            api_key: API key for AI provider (optional)
            
        Returns:
            Processing result dictionary
        """
        try:
            logger.info(f"Processing document: {document.filename}")
            
            # Update status to processing
            document.status = DocumentStatus.PROCESSING
            
            # Process the document
            result = await self.processor.process_document(
                file_path=document.file_path,
                mime_type=document.mime_type,
                ai_provider=ai_provider,
                api_key=api_key
            )
            
            if result["success"]:
                # Update document with extracted content
                document.extracted_text = result.get("extracted_text", "")
                document.summary = result.get("summary", "")
                document.status = DocumentStatus.READY
                
                logger.info(f"Successfully processed document: {document.filename}")
                
                return {
                    "success": True,
                    "message": "Document processed successfully",
                    "analysis": result.get("analysis", ""),
                    "metadata": result.get("metadata", {})
                }
            else:
                # Update document with error
                document.error_message = result.get("error", "Unknown processing error")
                document.status = DocumentStatus.ERROR
                
                logger.error(f"Failed to process document: {document.filename} - {result.get('error')}")
                
                return {
                    "success": False,
                    "error": result.get("error", "Processing failed"),
                    "message": "Failed to process document"
                }
                
        except Exception as e:
            logger.error(f"Error processing document {document.filename}: {str(e)}")
            
            # Update document with error
            document.error_message = str(e)
            document.status = DocumentStatus.ERROR
            
            return {
                "success": False,
                "error": str(e),
                "message": "Processing error occurred"
            }
    
    async def get_document_content(self, document: Document) -> str:
        """Get processed content of a document"""
        if document.extracted_text:
            return document.extracted_text
        
        # If no extracted text, try to process again
        result = await self.processor.process_document(
            file_path=document.file_path,
            mime_type=document.mime_type
        )
        
        return result.get("extracted_text", "")
    
    def is_image_file(self, mime_type: str) -> bool:
        """Check if the file is an image"""
        return mime_type.startswith('image/')
    
    def is_document_file(self, mime_type: str) -> bool:
        """Check if the file is a document"""
        document_types = {
            'application/pdf', 'text/plain', 'text/markdown',
            'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/csv', 'application/json'
        }
        return mime_type in document_types
