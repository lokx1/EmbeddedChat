# 🚀 Deploy Backend lên Railway

## Cách nhanh nhất

### 1. Cài đặt Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Đăng nhập
```bash
railway login
```

### 3. Deploy tự động (Windows)
```powershell
.\deploy-to-railway.ps1
```

### 4. Deploy thủ công
```bash
railway init    # Tạo project mới
railway up      # Deploy
```

## Cấu hình Database

### Tùy chọn 1: Railway PostgreSQL (Khuyến nghị)
1. **Thêm PostgreSQL service** trong Railway Dashboard
2. **Cấu hình DATABASE_URL**:
   ```bash
   railway variables set DATABASE_URL="postgresql+asyncpg://username:password@host:port/database"
   ```

### Tùy chọn 2: Migrate từ Local PostgreSQL
```powershell
# Chạy script tự động migrate
.\migrate-local-db.ps1
```

### Tùy chọn 3: External Database
- **Supabase**: `railway variables set DATABASE_URL="postgresql+asyncpg://postgres:[password]@[host]:5432/postgres"`
- **Neon**: `railway variables set DATABASE_URL="postgresql+asyncpg://[user]:[password]@[host]/[database]"`
- **Local với ngrok**: `railway variables set DATABASE_URL="postgresql+asyncpg://user:pass@ngrok-url:port/db"`

📖 Xem chi tiết: `railway-postgres-setup.md` và `external-database-setup.md`

## Cấu hình Environment Variables

```bash
# Security
railway variables set SECRET_KEY="your-super-secret-key"
railway variables set ALGORITHM="HS256"

# CORS (thay đổi domain frontend của bạn)
railway variables set BACKEND_CORS_ORIGINS="https://your-frontend-domain.com"

# AI Keys (nếu cần)
railway variables set OPENAI_API_KEY="your-openai-key"
railway variables set ANTHROPIC_API_KEY="your-anthropic-key"
```

## Kiểm tra

- **Health Check**: `https://your-app.railway.app/`
- **API Docs**: `https://your-app.railway.app/api/docs`
- **Logs**: `railway logs`

## Troubleshooting

- **Lỗi port**: Đảm bảo sử dụng `$PORT` trong Procfile
- **Lỗi database**: Kiểm tra `DATABASE_URL` và tạo PostgreSQL service
- **Lỗi import**: Kiểm tra `requirements.txt` và `runtime.txt`

## Files đã tạo

### Core Files
- `Procfile` - Cấu hình startup command
- `runtime.txt` - Python version
- `railway.json` - Railway configuration
- `start.sh` - Startup script với migration
- `env.example` - Environment variables template

### Scripts
- `deploy-to-railway.ps1` - Auto-deploy script
- `migrate-local-db.ps1` - Migrate database từ local
- `scripts/migrate-local-to-railway.py` - Python migration script

### Documentation
- `railway-setup.md` - Hướng dẫn chi tiết
- `railway-postgres-setup.md` - Setup PostgreSQL trên Railway
- `external-database-setup.md` - Sử dụng external database
