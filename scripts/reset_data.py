#!/usr/bin/env python3
"""
Reset database to clean state - keep users but remove conversations and documents
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def reset_data():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='long',
            password='long',
            database='EmbeddedAI'
        )
        
        print("Cleaning test data...")
        
        # Delete messages first (foreign key constraint)
        await conn.execute("DELETE FROM messages")
        print("✅ Cleared messages")
        
        # Delete conversations
        await conn.execute("DELETE FROM conversations")
        print("✅ Cleared conversations")
        
        # Delete documents
        await conn.execute("DELETE FROM documents")
        print("✅ Cleared documents")
        
        # Keep users table for authentication
        print("✅ Users table kept for authentication")
        
        # Verify cleanup
        conversations = await conn.fetchval("SELECT COUNT(*) FROM conversations")
        messages = await conn.fetchval("SELECT COUNT(*) FROM messages")
        documents = await conn.fetchval("SELECT COUNT(*) FROM documents")
        users = await conn.fetchval("SELECT COUNT(*) FROM users")
        
        print(f"\nDatabase state after cleanup:")
        print(f"Users: {users}")
        print(f"Conversations: {conversations}")
        print(f"Messages: {messages}")
        print(f"Documents: {documents}")
        
        await conn.close()
        print("\n✅ Database cleanup completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(reset_data())
