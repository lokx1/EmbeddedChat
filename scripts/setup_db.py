# Database setup script
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.core.config import settings
from src.models.database import Base
from src.models import user, conversation, message, document

async def create_tables():
    """Create all database tables"""
    print(f"Connecting to database: {settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://').split('@')[1]}")
    
    try:
        # Create engine
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
        
        # Create all tables
        async with engine.begin() as conn:
            print("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            
        print("✅ Database tables created successfully!")
        
        # Close engine
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

async def drop_tables():
    """Drop all database tables (BE CAREFUL!)"""
    print(f"Connecting to database: {settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://').split('@')[1]}")
    
    confirm = input("⚠️  This will DROP ALL TABLES! Type 'YES' to confirm: ")
    if confirm != "YES":
        print("Cancelled.")
        return
        
    try:
        # Create engine
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
        
        # Drop all tables
        async with engine.begin() as conn:
            print("Dropping tables...")
            await conn.run_sync(Base.metadata.drop_all)
            
        print("✅ Database tables dropped successfully!")
        
        # Close engine
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        sys.exit(1)

async def test_connection():
    """Test database connection"""
    print(f"Testing connection to: {settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://').split('@')[1]}")
    
    try:
        # Create engine
        engine = create_async_engine(settings.DATABASE_URL)
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"PostgreSQL version: {version}")
            
        # Close engine
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL is running")
        print("2. Database 'EmbeddedAI' exists")
        print("3. Username and password in .env file are correct")
        print("4. Database host and port are correct")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python setup_db.py test     - Test database connection")
        print("  python setup_db.py create   - Create all tables")
        print("  python setup_db.py drop     - Drop all tables")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "test":
        asyncio.run(test_connection())
    elif command == "create":
        asyncio.run(create_tables())
    elif command == "drop":
        asyncio.run(drop_tables())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
