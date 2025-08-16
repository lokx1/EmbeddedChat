#!/usr/bin/env python3
"""
PostgreSQL Migration Runner
Chạy migration cho chat tables trên PostgreSQL database
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from urllib.parse import urlparse

def get_database_config():
    """Get database configuration from environment variables or DATABASE_URL"""
    
    # Check if DATABASE_URL is provided
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Parse the DATABASE_URL
        # Format: postgresql+asyncpg://user:password@host:port/database
        # or: postgresql://user:password@host:port/database
        
        # Remove asyncpg part if present for psycopg2 compatibility
        if '+asyncpg' in database_url:
            database_url = database_url.replace('+asyncpg', '')
        
        parsed = urlparse(database_url)
        
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:] if parsed.path else 'postgres',  # Remove leading '/'
            'user': parsed.username,
            'password': parsed.password
        }
    else:
        # Fallback to individual env vars
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'EmbeddedAI'),
            'user': os.getenv('DB_USER', 'long'),
            'password': os.getenv('DB_PASSWORD', 'long')
        }

def run_migration():
    """Run the chat tables migration"""
    config = get_database_config()
    
    print("🗃️  PostgreSQL Chat Migration")
    print("=" * 50)
    print(f"Host: {config['host']}:{config['port']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    print("-" * 50)
    
    try:
        # Connect to PostgreSQL
        print("🔗 Connecting to PostgreSQL...")
        conn = psycopg2.connect(**config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Read migration file
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'add_chat_tables.sql')
        
        if not os.path.exists(migration_file):
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        print("📖 Reading migration file...")
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Execute migration
        print("⚡ Executing migration...")
        cursor.execute(migration_sql)
        
        # Verify tables were created
        print("✅ Verifying tables...")
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('chat_conversations', 'chat_messages')
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        if len(tables) == 2:
            print("✅ Tables created successfully:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("⚠️  Some tables may not have been created")
        
        # Check functions and triggers
        print("🔧 Verifying functions and triggers...")
        cursor.execute("""
            SELECT routine_name FROM information_schema.routines 
            WHERE routine_schema = 'public' 
            AND routine_name LIKE '%message_count%' OR routine_name LIKE '%conversation%'
            ORDER BY routine_name;
        """)
        
        functions = cursor.fetchall()
        print(f"✅ Functions created: {len(functions)}")
        for func in functions:
            print(f"   - {func[0]}")
        
        cursor.execute("""
            SELECT trigger_name FROM information_schema.triggers 
            WHERE event_object_table IN ('chat_messages', 'chat_conversations')
            ORDER BY trigger_name;
        """)
        
        triggers = cursor.fetchall()
        print(f"✅ Triggers created: {len(triggers)}")
        for trigger in triggers:
            print(f"   - {trigger[0]}")
        
        print("\n🎉 Migration completed successfully!")
        print("Your chat system is ready to use!")
        
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

def show_usage():
    """Show usage instructions"""
    print("\n📋 Cách sử dụng:")
    print("-" * 30)
    print("1. Cài đặt dependencies:")
    print("   pip install psycopg2-binary")
    print()
    print("2. Set DATABASE_URL environment variable:")
    print("   export DATABASE_URL=postgresql+asyncpg://long:long@localhost:5432/EmbeddedAI")
    print()
    print("   Hoặc set individual variables:")
    print("   export DB_HOST=localhost")
    print("   export DB_PORT=5432") 
    print("   export DB_NAME=EmbeddedAI")
    print("   export DB_USER=long")
    print("   export DB_PASSWORD=long")
    print()
    print("3. Chạy migration:")
    print("   python run_migration.py")
    print()
    print("Hoặc chạy trực tiếp bằng psql:")
    print("   psql -h localhost -U long -d EmbeddedAI -f migrations/add_chat_tables.sql")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        show_usage()
    else:
        success = run_migration()
        if not success:
            show_usage()
            sys.exit(1)
