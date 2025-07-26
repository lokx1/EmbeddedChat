import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import AsyncSessionLocal
from sqlalchemy import text

async def check_table_structure():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text('SELECT * FROM documents LIMIT 0'))
        print('Columns in documents table:')
        for col in result.keys():
            print(f'  - {col}')
        
        # Check column details
        result = await db.execute(text("""
            SELECT column_name, is_nullable, column_default, data_type
            FROM information_schema.columns 
            WHERE table_name = 'documents'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        print('\nColumn details:')
        for col_name, nullable, default, data_type in columns:
            print(f'  {col_name}: {data_type}, nullable={nullable}, default={default}')

if __name__ == "__main__":
    asyncio.run(check_table_structure())
