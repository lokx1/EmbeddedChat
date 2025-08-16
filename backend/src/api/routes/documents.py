# Document routes
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import os
import uuid
from pathlib import Path
import asyncio

from src.models.database import get_db
from src.models.user import User
from src.models.document import Document, DocumentStatus
from src.schemas.document import (
    DocumentCreate, Document as DocumentSchema,
    DocumentUpdate, DocumentList
)
from src.services.document.upload_service import UploadService
# from src.api.middleware.auth import get_current_active_user  # Disabled for testing
from src.core.config import settings

# Mock user function for testing
async def get_current_active_user():
    """Mock user function - replace with actual auth"""
    from src.models.user import User
    return User(id=1, username="test_user", email="test@example.com")

router = APIRouter(prefix="/documents", tags=["documents"])

# Configure upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_MIME_TYPES = {
    # Document types
    "text/plain",
    "text/markdown", 
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/csv",
    "application/json",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    
    # Image types for AI analysis
    "image/jpeg",
    "image/jpg", 
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff",
    "image/heic",
    "image/heif",
    
    # Video types supported by Gemini
    "video/mp4",
    "video/mpeg", 
    "video/mov",
    "video/avi",
    "video/x-flv",
    "video/mpg",
    "video/webm",
    "video/wmv",
    "video/3gpp",
    
    # Audio types supported by Gemini
    "audio/wav",
    "audio/mp3",
    "audio/aiff",
    "audio/aac",
    "audio/ogg",
    "audio/flac"
}

MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB for video/audio files


@router.post("/upload", response_model=DocumentSchema, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    ai_provider: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a document with optional AI analysis"""
    # Validate file type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed"
        )
    
    # Read file content to check size
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size {file_size} exceeds maximum allowed size {MAX_FILE_SIZE}"
        )
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create document record
    document = Document(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=file.content_type,
        user_id=current_user.id,
        status=DocumentStatus.UPLOADING
    )
    
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    # Process document with AI analysis if requested
    upload_service = UploadService()
    try:
        # Process in background
        processing_result = await upload_service.process_uploaded_document(
            document=document,
            ai_provider=ai_provider,
            api_key=api_key
        )
        
        # Save updated document
        await db.commit()
        await db.refresh(document)
        
    except Exception as e:
        # If processing fails, still return the document but with error status
        document.status = DocumentStatus.ERROR
        document.error_message = str(e)
        await db.commit()
    
    return document


@router.get("/", response_model=DocumentList)
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[DocumentStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's documents"""
    query = select(Document).where(Document.user_id == current_user.id)
    
    if status:
        query = query.where(Document.status == status)
    
    # Get total count
    count_result = await db.execute(
        select(Document).where(Document.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated results
    result = await db.execute(query.offset(skip).limit(limit))
    documents = result.scalars().all()
    
    return DocumentList(
        documents=documents,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific document"""
    result = await db.execute(
        select(Document).where(
            and_(
                Document.id == document_id,
                Document.user_id == current_user.id
            )
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.put("/{document_id}", response_model=DocumentSchema)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a document"""
    result = await db.execute(
        select(Document).where(
            and_(
                Document.id == document_id,
                Document.user_id == current_user.id
            )
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update fields
    for field, value in document_data.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    
    await db.commit()
    await db.refresh(document)
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document"""
    result = await db.execute(
        select(Document).where(
            and_(
                Document.id == document_id,
                Document.user_id == current_user.id
            )
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file from filesystem
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Error deleting file {document.file_path}: {e}")
    
    # Delete from database
    await db.delete(document)
    await db.commit()


@router.post("/{document_id}/analyze")
async def analyze_document(
    document_id: int,
    ai_provider: str = Form(...),
    api_key: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a document with AI"""
    # Get document
    result = await db.execute(
        select(Document).where(
            and_(
                Document.id == document_id,
                Document.user_id == current_user.id
            )
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Process document with AI
    upload_service = UploadService()
    try:
        processing_result = await upload_service.process_uploaded_document(
            document=document,
            ai_provider=ai_provider,
            api_key=api_key
        )
        
        await db.commit()
        await db.refresh(document)
        
        return {
            "success": processing_result["success"],
            "document": document,
            "analysis": processing_result.get("analysis", ""),
            "message": processing_result.get("message", "")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/{document_id}/content")
async def get_document_content(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get extracted content of a document"""
    # Get document
    result = await db.execute(
        select(Document).where(
            and_(
                Document.id == document_id,
                Document.user_id == current_user.id
            )
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    upload_service = UploadService()
    content = await upload_service.get_document_content(document)
    
    return {
        "document_id": document_id,
        "filename": document.original_filename,
        "content": content,
        "summary": document.summary,
        "status": document.status
    }
