# PostgreSQL Setup Guide

Hướng dẫn setup PostgreSQL database cho EmbeddedChat system với conversation management.

## 📋 Prerequisites

1. **PostgreSQL đã được cài đặt**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   
   # macOS with Homebrew
   brew install postgresql
   
   # Windows: Download từ https://www.postgresql.org/download/windows/
   ```

2. **Python PostgreSQL adapter**
   ```bash
   pip install psycopg2-binary
   ```

## 🗃️ Database Setup

### 1. Tạo Database
```bash
# Kết nối như postgres user
sudo -u postgres psql

# Hoặc
psql -U postgres

# Tạo database
CREATE DATABASE embeddedchat;

# Tạo user (optional)
CREATE USER embeddedchat_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE embeddedchat TO embeddedchat_user;

# Exit
\q
```

### 2. Environment Variables
Tạo file `.env` trong folder `backend/`:
```env
# Option 1: Sử dụng DATABASE_URL (Recommended)
DATABASE_URL=postgresql+asyncpg://long:long@localhost:5432/EmbeddedAI

# Option 2: Individual variables
DB_HOST=localhost
DB_PORT=5432
DB_NAME=EmbeddedAI
DB_USER=long
DB_PASSWORD=long
```

## 🚀 Chạy Migration

### Cách 1: Sử dụng Python Script (Recommended)
```bash
cd backend
python run_migration.py
```

### Cách 2: Sử dụng psql command line
```bash
cd backend
psql -h localhost -U long -d EmbeddedAI -f migrations/add_chat_tables.sql
```

### Cách 3: Từ PostgreSQL CLI
```bash
psql -U long -d EmbeddedAI
\i migrations/add_chat_tables.sql
\q
```

## ✅ Verification

Sau khi chạy migration, verify bằng các commands:

```sql
-- Kiểm tra tables
\dt

-- Kiểm tra structure của tables
\d chat_conversations
\d chat_messages

-- Kiểm tra functions
\df

-- Kiểm tra triggers
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
WHERE event_object_table IN ('chat_conversations', 'chat_messages');

-- Test insert data
INSERT INTO chat_conversations (title, user_id) VALUES ('Test Chat', 1);
SELECT * FROM chat_conversations;
```

## 🔧 Troubleshooting

### Lỗi connection refused
```bash
# Kiểm tra PostgreSQL service
sudo systemctl status postgresql

# Start service nếu cần
sudo systemctl start postgresql

# Enable auto-start
sudo systemctl enable postgresql
```

### Lỗi authentication failed
```bash
# Reset password cho postgres user
sudo -u postgres psql
ALTER USER postgres PASSWORD 'new_password';
```

### Lỗi database not exist
```bash
# Tạo database
createdb -U long EmbeddedAI
```

### Lỗi permission denied
```bash
# Grant permissions
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE EmbeddedAI TO long;
GRANT ALL ON SCHEMA public TO long;
```

## 📊 Database Schema

Migration sẽ tạo:

### Tables:
- `chat_conversations` - Conversation metadata và AI settings
- `chat_messages` - Individual messages với AI response metadata

### Functions:
- `update_conversation_updated_at()` - Auto-update conversation timestamp
- `increment_message_count()` - Auto-increment message count  
- `decrement_message_count()` - Auto-decrement khi delete

### Triggers:
- `trigger_update_conversation_updated_at` - Update timestamp khi có message mới
- `trigger_increment_message_count` - Tăng message count
- `trigger_decrement_message_count` - Giảm message count khi delete

### Indexes:
- Performance indexes trên user_id, conversation_id, timestamps

## 🔄 Rollback (nếu cần)

Nếu cần xóa tables:
```sql
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS chat_conversations CASCADE;
DROP FUNCTION IF EXISTS update_conversation_updated_at() CASCADE;
DROP FUNCTION IF EXISTS increment_message_count() CASCADE;
DROP FUNCTION IF EXISTS decrement_message_count() CASCADE;
```

## 📈 Next Steps

Sau khi migration thành công:

1. **Update backend config** để sử dụng PostgreSQL connection
2. **Restart backend service**
3. **Test chat functionality** qua frontend
4. **Monitor logs** để ensure everything works

## 💡 Tips

- Sử dụng `pgAdmin` cho GUI management
- Setup connection pooling với `psycopg2.pool`
- Consider backup strategy với `pg_dump`
- Monitor performance với `pg_stat_statements`
