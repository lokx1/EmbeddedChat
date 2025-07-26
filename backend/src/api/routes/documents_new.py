# Document routes with RAG and vector store integration
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from ...models.database import get_db
from ...models.user import User
from ...services.document.upload_service import upload_service
from ...services.document.storage_service import storage_service
from ...services.rag.retrieval_service import retrieval_service
from ...services.rag.vector_store import vector_store
from ...api.middleware.auth import get_current_active_user

router = APIRouter(prefix="/documents", tags=["documents"])

# Request/Response models
class DocumentUploadResponse(BaseModel):
    success: bool
    document_id: int
    filename: str
    status: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    size: int
    status: str
    uploaded_at: str
    summary: Optional[str] = None
    chunk_count: Optional[int] = None

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a document with RAG integration"""
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
            "text/csv"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not supported"
            )
        
        # Check file size (max 10MB)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size too large (max 10MB)"
            )
        
        # Reset file position for upload service
        await file.seek(0)
        
        result = await upload_service.upload_document(file, current_user.id, db)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return DocumentUploadResponse(
            success=True,
            document_id=result["document_id"],
            filename=result["filename"],
            status=result["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=List[DocumentResponse])
async def get_user_documents(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all documents for the current user"""
    try:
        documents = await upload_service.get_user_documents(current_user.id, db)
        return [DocumentResponse(**doc) for doc in documents]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document and its vector embeddings"""
    try:
        result = await upload_service.delete_document(document_id, current_user.id, db)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/search")
async def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Search documents using semantic search"""
    try:
        result = await retrieval_service.search_documents(
            request.query, current_user.id, db, request.max_results
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return {
            "results": result["results"],
            "context": result["context"],
            "total_chunks": result["total_chunks"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{document_id}/context")
async def get_document_context(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all chunks from a specific document"""
    try:
        result = await retrieval_service.get_document_context(
            document_id, current_user.id, db
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{document_id}/related")
async def get_related_documents(
    document_id: int,
    max_results: int = Query(3, ge=1, le=10),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get documents related to the specified document"""
    try:
        related = await retrieval_service.get_related_documents(
            document_id, current_user.id, db, max_results
        )
        
        return {"related_documents": related}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats")
async def get_document_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document storage statistics"""
    try:
        stats = await storage_service.get_storage_stats(db)
        vector_stats = await vector_store.get_collection_stats()
        
        return {
            **stats,
            "vector_store": vector_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
