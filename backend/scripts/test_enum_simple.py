import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import AsyncSessionLocal
from src.models.document import Document, DocumentStatus

async def test_enum_insert():
    async with AsyncSessionLocal() as db:
        try:
            print(f'DocumentStatus.READY value: {DocumentStatus.READY}')
            print(f'DocumentStatus.READY repr: {repr(DocumentStatus.READY)}')
            
            # Create a document with the enum
            document = Document(
                filename='test.pdf',
                original_filename='test.pdf',
                file_path='/test',
                file_size=1024,
                mime_type='application/pdf',
                user_id=10,
                status=DocumentStatus.READY,
                extracted_text='test',
                summary='test'
            )
            
            print(f'Document status before adding: {document.status}')
            db.add(document)
            await db.flush()  # This will trigger the SQL but not commit
            
            print(f'Document status after flush: {document.status}')
            
            await db.commit()
            print('Successfully inserted document')
            
        except Exception as e:
            print(f'Error: {e}')
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(test_enum_insert())
