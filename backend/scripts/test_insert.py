import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import AsyncSessionLocal
from sqlalchemy import text

async def test_insert():
    async with AsyncSessionLocal() as db:
        try:
            # Try inserting with each enum value
            for status in ['UPLOADING', 'PROCESSING', 'READY', 'ERROR']:
                print(f'Testing with status: {status}')
                try:
                    result = await db.execute(text("""
                        INSERT INTO documents (filename, original_filename, file_path, file_size, mime_type, status, user_id, extracted_text, summary, chunk_count, created_at)
                        VALUES ('test.pdf', 'test.pdf', '/test', 1024, 'application/pdf', :status, 10, 'test', 'test', 0, NOW())
                        RETURNING id
                    """), {"status": status})
                    doc_id = result.fetchone()[0]
                    print(f'✓ Successfully inserted with status {status}, id: {doc_id}')
                    
                    # Delete it
                    await db.execute(text("DELETE FROM documents WHERE id = :id"), {"id": doc_id})
                    await db.commit()
                except Exception as e:
                    print(f'✗ Failed with status {status}: {e}')
                    await db.rollback()
                    
        except Exception as e:
            print(f'Error: {e}')
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(test_insert())
