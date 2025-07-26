import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import AsyncSessionLocal
from sqlalchemy import text

async def test_default():
    async with AsyncSessionLocal() as db:
        try:
            # Let's try inserting without specifying status to use the default
            result = await db.execute(text("""
                INSERT INTO documents (filename, original_filename, file_path, file_size, mime_type, user_id, extracted_text, summary, chunk_count, created_at)
                VALUES ('test.pdf', 'test.pdf', '/test', 1024, 'application/pdf', 10, 'test', 'test', 0, NOW())
                RETURNING id, status
            """))
            doc_id, status = result.fetchone()
            print(f'Successfully inserted with default status: {status}')
            
            # Delete it
            await db.execute(text('DELETE FROM documents WHERE id = :id'), {'id': doc_id})
            await db.commit()
            
        except Exception as e:
            print(f'Error: {e}')
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(test_default())
