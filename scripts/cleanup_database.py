#!/usr/bin/env python3
"""
Clean up database - reset conversations, messages, documents to 0
Keep users for login testing
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.core.config import settings

async def cleanup_database():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        print("Cleaning up database...")
        
        # Delete in correct order due to foreign key constraints
        await conn.execute(text("DELETE FROM messages"))
        print("✅ Deleted all messages")
        
        await conn.execute(text("DELETE FROM conversations"))
        print("✅ Deleted all conversations")
        
        await conn.execute(text("DELETE FROM documents"))
        print("✅ Deleted all documents")
        
        # Reset auto-increment sequences
        await conn.execute(text("ALTER SEQUENCE messages_id_seq RESTART WITH 1"))
        await conn.execute(text("ALTER SEQUENCE conversations_id_seq RESTART WITH 1"))
        await conn.execute(text("ALTER SEQUENCE documents_id_seq RESTART WITH 1"))
        
        print("✅ Reset ID sequences")
        
        # Check final counts
        result = await conn.execute(text("SELECT COUNT(*) FROM users"))
        users_count = result.scalar()
        
        result = await conn.execute(text("SELECT COUNT(*) FROM conversations"))
        conversations_count = result.scalar()
        
        result = await conn.execute(text("SELECT COUNT(*) FROM messages"))
        messages_count = result.scalar()
        
        result = await conn.execute(text("SELECT COUNT(*) FROM documents"))
        documents_count = result.scalar()
        
        print(f"\nFinal counts:")
        print(f"Users: {users_count} (kept for login)")
        print(f"Conversations: {conversations_count}")
        print(f"Messages: {messages_count}")
        print(f"Documents: {documents_count}")
        
        print("\n🎉 Database cleanup completed!")

if __name__ == "__main__":
    asyncio.run(cleanup_database())
