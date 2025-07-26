import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import AsyncSessionLocal
from sqlalchemy import text

async def investigate_constraint():
    async with AsyncSessionLocal() as db:
        # Get constraint details with modern PostgreSQL syntax
        result = await db.execute(text("""
            SELECT conname, 
                   pg_get_constraintdef(oid) as constraint_def
            FROM pg_constraint 
            WHERE conrelid = 'documents'::regclass
            AND contype = 'c'
        """))
        constraints = result.fetchall()
        print('Check constraints:')
        for name, definition in constraints:
            print(f'  {name}: {definition}')
        
        # Also check what values are actually in the enum type
        result = await db.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid 
                FROM pg_type 
                WHERE typname = 'documentstatus'
            )
            ORDER BY enumsortorder
        """))
        enum_values = result.fetchall()
        print('\nActual enum values in database:')
        for (value,) in enum_values:
            print(f'  {repr(value)}')

if __name__ == "__main__":
    asyncio.run(investigate_constraint())
