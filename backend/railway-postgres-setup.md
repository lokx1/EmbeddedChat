# 🗄️ Setup PostgreSQL trên Railway

## Bước 1: Tạo PostgreSQL Service

1. **Vào Railway Dashboard**
2. **Tạo project mới** (nếu chưa có):
   - Click "New Project"
   - Chọn "Deploy from GitHub" hoặc "Start from scratch"

3. **Thêm PostgreSQL service**:
   - Click "New Service"
   - Chọn "Database" → "PostgreSQL"
   - Railway sẽ tự động tạo database cho bạn

## Bước 2: Lấy thông tin kết nối

1. **Vào PostgreSQL service** trong Railway Dashboard
2. **Copy connection string**:
   - Vào tab "Connect"
   - Copy "Postgres Connection URL"
   - Format: `postgresql://username:password@host:port/database`

## Bước 3: Cấu hình Environment Variables

```bash
# Cấu hình DATABASE_URL
railway variables set DATABASE_URL="postgresql+asyncpg://username:password@host:port/database"
```

## Bước 4: Export dữ liệu từ local (nếu cần)

### Export từ local PostgreSQL:
```bash
# Export toàn bộ database
pg_dump -h localhost -U your_username -d your_database > backup.sql

# Hoặc export chỉ schema
pg_dump -h localhost -U your_username -d your_database --schema-only > schema.sql

# Hoặc export chỉ data
pg_dump -h localhost -U your_username -d your_database --data-only > data.sql
```

### Import vào Railway PostgreSQL:
```bash
# SSH vào Railway
railway shell

# Import data
psql $DATABASE_URL < backup.sql
```

## Bước 5: Chạy Migration

```bash
# SSH vào Railway
railway shell

# Chạy migration
python run_migration.py
```

## Bước 6: Kiểm tra kết nối

```bash
# SSH vào Railway
railway shell

# Test connection
python -c "
import asyncio
from src.models.database import engine

async def test_db():
    try:
        async with engine.begin() as conn:
            result = await conn.execute('SELECT 1')
            print('✅ Database connection successful!')
    except Exception as e:
        print(f'❌ Database connection failed: {e}')

asyncio.run(test_db())
"
```
