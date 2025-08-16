#!/usr/bin/env python3
"""
Fix database status enum constraint
"""
import asyncio
from src.models.database import engine
from sqlalchemy import text

async def fix_enum():
    """Fix enum values in database"""
    try:
        async with engine.connect() as conn:
            print("🔧 Fixing database enum...")
            
            # First, check current enum values
            result = await conn.execute(text("""
                SELECT e.enumlabel 
                FROM pg_enum e 
                JOIN pg_type t ON e.enumtypid = t.oid 
                WHERE t.typname = 'documentstatus'
                ORDER BY e.enumsortorder
            """))
            
            current_values = [row[0] for row in result.fetchall()]
            print(f"Current enum values: {current_values}")
            
            # Define the values we need
            needed_values = ['uploading', 'processing', 'ready', 'error']
            
            # Add missing values
            for value in needed_values:
                if value not in current_values:
                    print(f"Adding enum value: {value}")
                    await conn.execute(text(f"ALTER TYPE documentstatus ADD VALUE '{value}'"))
            
            await conn.commit()
            print("✅ Database enum fixed!")
            
    except Exception as e:
        print(f"❌ Failed to fix enum: {e}")
        print("Trying alternative fix...")
        
        # Alternative: Drop and recreate constraint
        try:
            async with engine.connect() as conn:
                # Remove check constraint
                await conn.execute(text("ALTER TABLE documents DROP CONSTRAINT IF EXISTS documents_status_check"))
                await conn.commit()
                print("✅ Removed problematic constraint")
        except Exception as e2:
            print(f"❌ Alternative fix failed: {e2}")

if __name__ == "__main__":
    asyncio.run(fix_enum())
