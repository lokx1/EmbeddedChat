# 🌐 Sử dụng External Database với Railway

## Tùy chọn 1: PostgreSQL Local (Cần expose ra internet)

### Bước 1: Expose PostgreSQL local ra internet

#### Sử dụng ngrok:
```bash
# Cài đặt ngrok
# Download từ https://ngrok.com/

# Expose PostgreSQL port
ngrok tcp 5432
```

#### Hoặc sử dụng Cloudflare Tunnel:
```bash
# Cài đặt cloudflared
# Download từ https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Tạo tunnel
cloudflared tunnel create railway-db
cloudflared tunnel route dns railway-db your-db.your-domain.com

# Expose PostgreSQL
cloudflared tunnel run --url tcp://localhost:5432 railway-db
```

### Bước 2: Cấu hình PostgreSQL để accept external connections

#### Chỉnh sửa postgresql.conf:
```conf
# Tìm và uncomment dòng này
listen_addresses = '*'
```

#### Chỉnh sửa pg_hba.conf:
```conf
# Thêm dòng này để cho phép kết nối từ bất kỳ đâu (chỉ cho development)
host    all             all             0.0.0.0/0               md5
```

#### Restart PostgreSQL:
```bash
# Windows
net stop postgresql
net start postgresql

# Linux/Mac
sudo systemctl restart postgresql
```

### Bước 3: Cấu hình Railway

```bash
# Sử dụng ngrok URL
railway variables set DATABASE_URL="postgresql+asyncpg://username:password@ngrok-url:port/database"

# Hoặc sử dụng Cloudflare Tunnel
railway variables set DATABASE_URL="postgresql+asyncpg://username:password@your-db.your-domain.com:port/database"
```

## Tùy chọn 2: Cloud Database (Khuyến nghị cho production)

### Supabase (Free tier):
1. Tạo account tại https://supabase.com
2. Tạo project mới
3. Lấy connection string từ Settings → Database
4. Cấu hình Railway:
```bash
railway variables set DATABASE_URL="postgresql+asyncpg://postgres:[password]@[host]:5432/postgres"
```

### Neon (Free tier):
1. Tạo account tại https://neon.tech
2. Tạo project mới
3. Lấy connection string
4. Cấu hình Railway:
```bash
railway variables set DATABASE_URL="postgresql+asyncpg://[user]:[password]@[host]/[database]"
```

### PlanetScale (MySQL):
1. Tạo account tại https://planetscale.com
2. Tạo database
3. Lấy connection string
4. Cấu hình Railway:
```bash
railway variables set DATABASE_URL="mysql+asyncmy://[user]:[password]@[host]:3306/[database]"
```

## Tùy chọn 3: Railway PostgreSQL với Data Migration

### Bước 1: Export data từ local
```bash
# Export schema
pg_dump -h localhost -U your_username -d your_database --schema-only > schema.sql

# Export data
pg_dump -h localhost -U your_username -d your_database --data-only > data.sql

# Export everything
pg_dump -h localhost -U your_username -d your_database > full_backup.sql
```

### Bước 2: Tạo Railway PostgreSQL
1. Vào Railway Dashboard
2. Tạo PostgreSQL service
3. Lấy connection string

### Bước 3: Import data
```bash
# SSH vào Railway
railway shell

# Import schema trước
psql $DATABASE_URL < schema.sql

# Import data
psql $DATABASE_URL < data.sql
```

### Bước 4: Cấu hình Railway
```bash
railway variables set DATABASE_URL="postgresql+asyncpg://[railway-connection-string]"
```

## Kiểm tra kết nối

Tạo script test:
```bash
# Tạo file test_db.py
cat > test_db.py << 'EOF'
import asyncio
import os
from src.models.database import engine

async def test_db():
    try:
        async with engine.begin() as conn:
            result = await conn.execute('SELECT 1')
            print('✅ Database connection successful!')
            print(f'Database URL: {os.getenv("DATABASE_URL", "Not set")}')
    except Exception as e:
        print(f'❌ Database connection failed: {e}')

if __name__ == "__main__":
    asyncio.run(test_db())
EOF

# Chạy test
python test_db.py
```

## Troubleshooting

### Lỗi kết nối:
1. **Kiểm tra firewall**: Đảm bảo port 5432 được mở
2. **Kiểm tra PostgreSQL config**: Đảm bảo `listen_addresses = '*'`
3. **Kiểm tra pg_hba.conf**: Đảm bảo cho phép kết nối từ external
4. **Kiểm tra ngrok/cloudflared**: Đảm bảo tunnel đang chạy

### Lỗi SSL:
```bash
# Thêm SSL mode vào connection string
railway variables set DATABASE_URL="postgresql+asyncpg://user:pass@host:port/db?sslmode=require"
```

### Lỗi timeout:
```bash
# Thêm timeout vào connection string
railway variables set DATABASE_URL="postgresql+asyncpg://user:pass@host:port/db?connect_timeout=10"
```
