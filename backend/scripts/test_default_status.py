import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import AsyncSessionLocal
from src.models.document import Document, DocumentStatus

async def test_default_status():
    async with AsyncSessionLocal() as db:
        try:
            # Create a document without specifying status (let it use default)
            document = Document(
                filename='test.pdf',
                original_filename='test.pdf',
                file_path='/test',
                file_size=1024,
                mime_type='application/pdf',
                user_id=10,
                extracted_text='test',
                summary='test'
            )
            
            print(f'Document status before adding: {document.status}')
            db.add(document)
            await db.flush()
            
            print(f'Document status after flush: {document.status}')
            await db.commit()
            print('Successfully inserted document with default status')
            
            # Clean up
            await db.delete(document)
            await db.commit()
            
        except Exception as e:
            print(f'Error: {e}')
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(test_default_status())
