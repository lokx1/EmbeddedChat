import os
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from ...models.document import Document, DocumentStatus
from ...services.rag.document_processor import document_processor
from ...services.rag.embedding_service import embedding_service
from ...services.rag.vector_store import vector_store
from .storage_service import storage_service
from ...utils.logger import get_logger

logger = get_logger(__name__)


class DocumentUploadService:
    """Handle document upload and processing pipeline"""
    
    async def upload_document(
        self, 
        file: UploadFile, 
        user_id: int, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Complete document upload and processing pipeline"""
        try:
            # Read file content
            content = await file.read()
            
            # Save file to storage
            storage_result = await storage_service.save_uploaded_file(
                content, file.filename, user_id
            )
            
            if not storage_result["success"]:
                return {"success": False, "error": storage_result["error"]}
            
            # Create document record in database
            document = Document(
                filename=storage_result["filename"],
                original_filename=file.filename,
                file_path=storage_result["file_path"],
                file_size=storage_result["file_size"],
                mime_type=file.content_type or "application/octet-stream",
                user_id=user_id,
                status=DocumentStatus.UPLOADING
            )
            
            db.add(document)
            await db.commit()
            await db.refresh(document)
            
            # Process document in background
            await self._process_document(document, db)
            
            return {
                "success": True,
                "document_id": document.id,
                "filename": document.filename,
                "status": document.status
            }
            
        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_document(self, document: Document, db: AsyncSession):
        """Process document: extract text, create embeddings, store in vector DB"""
        try:
            # Update status to processing
            document.status = DocumentStatus.PROCESSING
            await db.commit()
            
            # Extract text from document
            extract_result = document_processor.extract_text(
                document.file_path, 
                document.mime_type
            )
            
            if not extract_result["success"]:
                document.status = DocumentStatus.ERROR
                document.error_message = extract_result["error"]
                await db.commit()
                return
            
            extracted_text = extract_result["text"]
            document.extracted_text = extracted_text
            
            # Generate summary
            document.summary = document_processor.generate_summary(extracted_text)
            
            # Process text for vector storage
            process_result = await embedding_service.process_document_text(
                extracted_text,
                str(document.id),
                document.filename
            )
            
            if not process_result["success"]:
                document.status = DocumentStatus.ERROR
                document.error_message = process_result["error"]
                await db.commit()
                return
            
            # Store in vector database
            vector_result = await vector_store.add_documents(
                documents=process_result["chunks"],
                metadatas=process_result["metadatas"],
                ids=process_result["chunk_ids"]
            )
            
            if not vector_result:
                document.status = DocumentStatus.ERROR
                document.error_message = "Failed to store in vector database"
                await db.commit()
                return
            
            # Update document with processing results
            document.status = DocumentStatus.READY
            document.chunk_count = process_result["chunk_count"]
            document.embedding_model = "all-MiniLM-L6-v2"
            
            await db.commit()
            
            logger.info(f"Successfully processed document {document.id}")
            
        except Exception as e:
            logger.error(f"Failed to process document {document.id}: {e}")
            document.status = DocumentStatus.ERROR
            document.error_message = str(e)
            await db.commit()
    
    async def delete_document(self, document_id: int, user_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Delete document and its vector embeddings"""
        try:
            # Get document
            from sqlalchemy import select
            result = await db.execute(
                select(Document).where(
                    Document.id == document_id,
                    Document.user_id == user_id
                )
            )
            document = result.scalar_one_or_none()
            
            if not document:
                return {"success": False, "error": "Document not found"}
            
            # Delete from vector store
            await vector_store.delete_document(str(document_id))
            
            # Delete file from storage
            await storage_service.delete_file(document.file_path)
            
            # Delete from database
            await db.delete(document)
            await db.commit()
            
            return {"success": True, "message": "Document deleted successfully"}
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_documents(self, user_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get all documents for a user"""
        try:
            from sqlalchemy import select
            result = await db.execute(
                select(Document).where(Document.user_id == user_id)
            )
            documents = result.scalars().all()
            
            return [
                {
                    "id": doc.id,
                    "filename": doc.original_filename,
                    "size": doc.file_size,
                    "status": doc.status,
                    "uploaded_at": doc.created_at.isoformat(),
                    "summary": doc.summary,
                    "chunk_count": doc.chunk_count
                }
                for doc in documents
            ]
            
        except Exception as e:
            logger.error(f"Failed to get user documents: {e}")
            return []


# Global upload service instance
upload_service = DocumentUploadService()
