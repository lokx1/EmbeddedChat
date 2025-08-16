#!/usr/bin/env python3
"""
Check database constraints and enum values
"""
import asyncio
from src.models.database import engine
from sqlalchemy import text

async def check_db():
    try:
        async with engine.connect() as conn:
            # Check constraints
            print("🔍 Checking database constraints...")
            result = await conn.execute(text("""
                SELECT conname, consrc 
                FROM pg_constraint 
                WHERE conname LIKE '%documents_status%'
            """))
            
            rows = result.fetchall()
            if rows:
                print('Database constraints:')
                for row in rows:
                    print(f'  {row[0]}: {row[1]}')
            else:
                print('No status constraints found')
            
            # Check enum type
            print("\n🔍 Checking enum values...")
            result2 = await conn.execute(text("""
                SELECT t.typname, e.enumlabel 
                FROM pg_enum e 
                JOIN pg_type t ON e.enumtypid = t.oid 
                WHERE t.typname LIKE '%document%'
                ORDER BY e.enumsortorder
            """))
            
            enum_rows = result2.fetchall()
            if enum_rows:
                print('Database enum values:')
                for row in enum_rows:
                    print(f'  {row[0]}: {row[1]}')
            else:
                print('No document enum found')

            # Check actual table structure
            print("\n🔍 Checking table structure...")
            result3 = await conn.execute(text("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns 
                WHERE table_name = 'documents' AND column_name = 'status'
            """))
            
            col_rows = result3.fetchall()
            for row in col_rows:
                print(f'Column: {row[0]}, Type: {row[1]}, UDT: {row[2]}')

    except Exception as e:
        print(f"❌ Database check failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
