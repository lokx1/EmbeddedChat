import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import AsyncSessionLocal
from sqlalchemy import text

async def clear_database():
    async with AsyncSessionLocal() as db:
        try:
            print("Clearing all data from database...")
            
            # Delete in correct order to avoid foreign key constraints
            tables_to_clear = [
                'documents',
                'messages', 
                'conversations',
                'users'
            ]
            
            for table in tables_to_clear:
                result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                print(f"  {table}: {count} records")
                
                await db.execute(text(f"DELETE FROM {table}"))
                
            await db.commit()
            print("\n✅ Database cleared successfully!")
            print("You can now test registration and login from scratch.")
            
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(clear_database())
