# Hướng dẫn Deploy Backend lên Railway

## Bước 1: Chuẩn bị

1. **Cài đặt Railway CLI** (nếu chưa có):
   ```bash
   npm install -g @railway/cli
   ```

2. **Đăng nhập Railway**:
   ```bash
   railway login
   ```

## Bước 2: Tạo Project trên Railway

1. **Tạo project mới**:
   ```bash
   railway init
   ```

2. **Hoặc kết nối với project hiện có**:
   ```bash
   railway link
   ```

## Bước 3: Cấu hình Database

1. **Thêm PostgreSQL service**:
   - Vào Railway Dashboard
   - Click "New Service" → "Database" → "PostgreSQL"
   - Ghi nhớ thông tin kết nối

2. **Cấu hình biến môi trường**:
   ```bash
   railway variables set DATABASE_URL="postgresql+asyncpg://username:password@host:port/database"
   ```

## Bước 4: Cấu hình Redis (Optional)

1. **Thêm Redis service** (nếu cần):
   - Vào Railway Dashboard
   - Click "New Service" → "Database" → "Redis"
   - Cấu hình biến môi trường:
   ```bash
   railway variables set REDIS_URL="redis://username:password@host:port"
   ```

## Bước 5: Cấu hình các biến môi trường khác

```bash
# Security
railway variables set SECRET_KEY="your-super-secret-key-here"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"

# CORS
railway variables set BACKEND_CORS_ORIGINS="https://your-frontend-domain.com"

# Rate Limiting
railway variables set RATE_LIMIT_REQUESTS="100"
railway variables set RATE_LIMIT_PERIOD="60"

# Email (nếu cần)
railway variables set SMTP_SERVER="smtp.gmail.com"
railway variables set SMTP_PORT="587"
railway variables set SMTP_USE_TLS="true"
railway variables set SMTP_USERNAME="your-email@gmail.com"
railway variables set SMTP_PASSWORD="your-app-password"
railway variables set SMTP_FROM_EMAIL="your-email@gmail.com"

# AI Provider API Keys (nếu cần)
railway variables set OPENAI_API_KEY="your-openai-key"
railway variables set ANTHROPIC_API_KEY="your-anthropic-key"
railway variables set GOOGLE_API_KEY="your-google-key"
```

## Bước 6: Deploy

1. **Deploy lên Railway**:
   ```bash
   railway up
   ```

2. **Hoặc deploy từ GitHub**:
   - Push code lên GitHub
   - Kết nối repository với Railway
   - Railway sẽ tự động deploy khi có commit mới

## Bước 7: Chạy Migration

1. **SSH vào Railway**:
   ```bash
   railway shell
   ```

2. **Chạy migration**:
   ```bash
   python run_migration.py
   ```

## Bước 8: Kiểm tra

1. **Kiểm tra logs**:
   ```bash
   railway logs
   ```

2. **Kiểm tra health check**:
   - Truy cập: `https://your-app-name.railway.app/`

3. **Kiểm tra API docs**:
   - Truy cập: `https://your-app-name.railway.app/api/docs`

## Troubleshooting

### Lỗi thường gặp:

1. **Port binding error**:
   - Đảm bảo sử dụng `$PORT` trong Procfile
   - Kiểm tra file `main.py` có sử dụng `0.0.0.0` cho host

2. **Database connection error**:
   - Kiểm tra `DATABASE_URL` có đúng format không
   - Đảm bảo database service đã được tạo và running

3. **Import error**:
   - Kiểm tra `requirements.txt` có đầy đủ dependencies
   - Đảm bảo Python version trong `runtime.txt` phù hợp

### Commands hữu ích:

```bash
# Xem logs real-time
railway logs --follow

# Restart service
railway service restart

# Xem thông tin service
railway status

# Xem biến môi trường
railway variables
```

## Cấu hình Custom Domain (Optional)

1. Vào Railway Dashboard
2. Chọn service của bạn
3. Vào tab "Settings"
4. Thêm custom domain trong phần "Domains"

## Monitoring

Railway cung cấp monitoring cơ bản:
- CPU usage
- Memory usage
- Network traffic
- Logs
- Health checks

## Scaling

Để scale ứng dụng:
1. Vào Railway Dashboard
2. Chọn service
3. Vào tab "Settings"
4. Điều chỉnh "Scale" settings
