import os
import shutil
import aiofiles
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ...models.document import Document, DocumentStatus
from ...utils.logger import get_logger

logger = get_logger(__name__)


class DocumentStorageService:
    def __init__(self):
        self.upload_dir = os.path.join(os.getcwd(), "data", "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_uploaded_file(
        self, 
        file_content: bytes, 
        filename: str, 
        user_id: int
    ) -> Dict[str, Any]:
        """Save uploaded file to storage"""
        try:
            # Create user-specific directory
            user_dir = os.path.join(self.upload_dir, str(user_id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Generate unique filename to avoid conflicts
            base_name, ext = os.path.splitext(filename)
            counter = 1
            unique_filename = filename
            file_path = os.path.join(user_dir, unique_filename)
            
            while os.path.exists(file_path):
                unique_filename = f"{base_name}_{counter}{ext}"
                file_path = os.path.join(user_dir, unique_filename)
                counter += 1
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            file_size = len(file_content)
            
            logger.info(f"Saved file {unique_filename} for user {user_id}")
            
            return {
                "success": True,
                "filename": unique_filename,
                "file_path": file_path,
                "file_size": file_size
            }
            
        except Exception as e:
            logger.error(f"Failed to save file {filename}: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    async def get_file_content(self, file_path: str) -> Optional[bytes]:
        """Get file content"""
        try:
            if not os.path.exists(file_path):
                return None
                
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            return content
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    async def get_storage_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            # Get document count and total size from database
            result = await db.execute(
                select(
                    func.count(Document.id).label('total_documents'),
                    func.sum(Document.file_size).label('total_size'),
                    func.count().filter(Document.status == DocumentStatus.READY).label('indexed_count')
                )
            )
            stats = result.first()
            
            total_documents = stats.total_documents or 0
            total_size = stats.total_size or 0
            indexed_count = stats.indexed_count or 0
            
            # Calculate storage used in GB
            storage_gb = round(total_size / (1024 * 1024 * 1024), 2)
            
            # Get categories (simple count by mime type)
            category_result = await db.execute(
                select(func.count(func.distinct(Document.mime_type)))
            )
            categories = category_result.scalar() or 0
            
            return {
                "total_documents": total_documents,
                "storage_used": f"{storage_gb} GB",
                "storage_bytes": total_size,
                "indexed": indexed_count,
                "categories": categories
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {
                "total_documents": 0,
                "storage_used": "0 GB",
                "storage_bytes": 0,
                "indexed": 0,
                "categories": 0
            }


# Global storage service instance
storage_service = DocumentStorageService()
