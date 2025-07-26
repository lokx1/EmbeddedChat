import asyncio
from datetime import datetime, timedelta
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.models.database import AsyncSessionLocal
from src.models.user import User
from src.models.document import Document, DocumentStatus

async def create_documents():
    async with AsyncSessionLocal() as db:
        # Get users with correct syntax
        result = await db.execute(select(User.id))
        user_rows = result.fetchall()
        
        if not user_rows:
            print("No users found. Please create users first.")
            return
        
        # Extract user IDs properly
        user_ids = [row[0] for row in user_rows]
        print(f'Found {len(user_ids)} users: {user_ids}')
        
        # Check existing documents
        doc_result = await db.execute(select(Document))
        existing_docs = doc_result.fetchall()
        
        print(f'Found {len(existing_docs)} existing documents')
        
        document_names = [
            'API Documentation.pdf',
            'User Guide.docx', 
            'Technical Specifications.md',
            'Database Schema.sql',
            'Project Requirements.txt',
            'Installation Guide.pdf',
            'Troubleshooting Manual.docx',
            'Code Examples.py',
            'Architecture Overview.md',
            'Security Guidelines.pdf'
        ]
        
        categories = ['Technical', 'Business', 'Personal', 'Documentation']
        
        for i, doc_name in enumerate(document_names):
            days_ago = random.randint(0, 60)
            uploaded_at = datetime.utcnow() - timedelta(days=days_ago)
            
            document = Document(
                filename=doc_name,
                original_filename=doc_name,
                file_path=f'/uploads/{doc_name.lower().replace(" ", "_")}',
                file_size=random.randint(1024, 5242880),
                mime_type='application/pdf' if doc_name.endswith('.pdf') else 'text/plain',
                user_id=random.choice(user_ids),
                status=DocumentStatus.READY,  # Use correct enum value
                extracted_text=f'This is extracted text from {doc_name}. It contains information about {random.choice(categories).lower()} topics.',
                summary=f'Summary of {doc_name}',
                created_at=uploaded_at
            )
            db.add(document)
        
        await db.commit()
        print('Created 10 sample documents')

if __name__ == "__main__":
    asyncio.run(create_documents())
