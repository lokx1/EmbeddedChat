import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import AsyncSessionLocal
from sqlalchemy import text

async def check_constraints():
    async with AsyncSessionLocal() as db:
        try:
            # Check enum values
            result = await db.execute(text("SELECT unnest(enum_range(NULL::documentstatus))"))
            values = result.fetchall()
            print('Allowed enum values:', [v[0] for v in values])
            
            # Check constraints
            result = await db.execute(text("""
                SELECT conname, consrc 
                FROM pg_constraint 
                WHERE conrelid = 'documents'::regclass
                AND contype = 'c'
            """))
            constraints = result.fetchall()
            for name, source in constraints:
                print(f'Constraint {name}: {source}')
                
            # Let's try inserting a single document manually to see what happens
            result = await db.execute(text("""
                INSERT INTO documents (filename, original_filename, file_path, file_size, mime_type, status, user_id, extracted_text, summary, chunk_count, created_at)
                VALUES ('test.pdf', 'test.pdf', '/test', 1024, 'application/pdf', 'UPLOADING', 10, 'test', 'test', 0, NOW())
                RETURNING id
            """))
            doc_id = result.fetchone()[0]
            print(f'Successfully inserted document with id: {doc_id}')
            
            # Delete it
            await db.execute(text("DELETE FROM documents WHERE id = :id"), {"id": doc_id})
            await db.commit()
            
        except Exception as e:
            print(f'Error: {e}')
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(check_constraints())
