#!/usr/bin/env python3
"""
Clean database - remove all test data
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def clean_database():
    # Parse DATABASE_URL
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://long:long@localhost:5432/EmbeddedAI")
    
    # Extract connection params from URL
    url_parts = database_url.replace("postgresql+asyncpg://", "").split("/")
    db_name = url_parts[1]
    
    host_part = url_parts[0].split("@")[1]
    user_part = url_parts[0].split("@")[0]
    
    host, port = host_part.split(":")
    user, password = user_part.split(":")
    
    print("🧹 Cleaning database...")
    
    try:
        conn = await asyncpg.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db_name
        )
        
        # Delete all data from tables (in correct order due to foreign keys)
        await conn.execute("DELETE FROM messages")
        await conn.execute("DELETE FROM conversations") 
        await conn.execute("DELETE FROM documents")
        await conn.execute("DELETE FROM users")
        
        print("✅ Database cleaned successfully!")
        print("All users, conversations, messages, and documents have been removed.")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")

if __name__ == "__main__":
    asyncio.run(clean_database())
