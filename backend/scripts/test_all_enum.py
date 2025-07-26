import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import AsyncSessionLocal
from sqlalchemy import text

async def test_all_enum_values():
    async with AsyncSessionLocal() as db:
        test_values = [
            'uploading', 'UPLOADING', 
            'processing', 'PROCESSING',
            'ready', 'READY',
            'error', 'ERROR'
        ]
        
        for value in test_values:
            try:
                result = await db.execute(text("""
                    INSERT INTO documents (filename, original_filename, file_path, file_size, mime_type, status, user_id, extracted_text, summary, chunk_count, created_at)
                    VALUES ('test.pdf', 'test.pdf', '/test', 1024, 'application/pdf', :status, 10, 'test', 'test', 0, NOW())
                    RETURNING id
                """), {"status": value})
                doc_id = result.fetchone()[0]
                print(f'✓ {value} - SUCCESS (id: {doc_id})')
                
                # Delete it
                await db.execute(text("DELETE FROM documents WHERE id = :id"), {"id": doc_id})
                await db.commit()
                
            except Exception as e:
                print(f'✗ {value} - FAILED: {str(e)[:100]}...')
                await db.rollback()

if __name__ == "__main__":
    asyncio.run(test_all_enum_values())
