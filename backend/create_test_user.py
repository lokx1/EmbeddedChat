#!/usr/bin/env python3
"""
Create Test User for Chat System
"""
import os
import asyncio
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from urllib.parse import urlparse

def get_database_config():
    """Get database configuration from environment variables or DATABASE_URL"""
    
    # Check if DATABASE_URL is provided
    database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://long:long@localhost:5432/EmbeddedAI')
    
    # Remove asyncpg part if present for psycopg2 compatibility
    if '+asyncpg' in database_url:
        database_url = database_url.replace('+asyncpg', '')
    
    parsed = urlparse(database_url)
    
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path[1:] if parsed.path else 'postgres',
        'user': parsed.username,
        'password': parsed.password
    }

def create_test_user():
    """Create a test user for chat system"""
    config = get_database_config()
    
    print("👤 Creating Test User for Chat System")
    print("=" * 50)
    print(f"Database: {config['database']}")
    print("-" * 50)
    
    try:
        # Connect to PostgreSQL
        print("🔗 Connecting to PostgreSQL...")
        conn = psycopg2.connect(**config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if users table exists
        print("🔍 Checking if users table exists...")
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'users';
        """)
        
        users_table = cursor.fetchone()
        
        if not users_table:
            print("⚠️  Users table doesn't exist. Creating it...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_superuser BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ Users table created!")
        
        # Check if test user already exists
        print("🔍 Checking if test user exists...")
        cursor.execute("SELECT id, username FROM users WHERE id = 1;")
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"✅ Test user already exists: ID={existing_user[0]}, Username={existing_user[1]}")
        else:
            # Create test user
            print("👤 Creating test user...")
            cursor.execute("""
                INSERT INTO users (id, username, email, hashed_password, full_name, is_active, is_superuser)
                VALUES (1, 'test_user', 'test@embeddedchat.com', 'hashed_password_placeholder', 'Test User', TRUE, FALSE)
                ON CONFLICT (id) DO NOTHING;
            """)
            
            # Also try without explicit ID in case of auto-increment issues
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser)
                VALUES ('chat_user', 'chat@embeddedchat.com', 'hashed_password_placeholder', 'Chat Test User', TRUE, FALSE)
                ON CONFLICT (username) DO NOTHING;
            """)
            
            print("✅ Test users created!")
        
        # Show all users
        print("\n📋 Current users in database:")
        cursor.execute("SELECT id, username, email, is_active FROM users ORDER BY id;")
        users = cursor.fetchall()
        
        if users:
            print("   ID | Username      | Email                    | Active")
            print("   ---|---------------|--------------------------|-------")
            for user in users:
                print(f"   {user[0]:2} | {user[1]:13} | {user[2]:24} | {user[3]}")
        else:
            print("   No users found")
        
        print("\n🎉 Test user setup completed!")
        print("You can now use the chat system!")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = create_test_user()
    if not success:
        exit(1)
