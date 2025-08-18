# 🚀 Hướng dẫn Deploy lên Vercel

## Bước 1: Kiểm tra dự án
```bash
cd frontend
npm run deploy-check
```

## Bước 2: Push code lên GitHub
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

## Bước 3: Deploy trên Vercel

### Cách 1: Deploy qua Vercel Dashboard
1. Truy cập [vercel.com](https://vercel.com)
2. Đăng nhập với GitHub
3. Click "New Project"
4. Import repository
5. Cấu hình:
   - **Framework**: Vite
   - **Root Directory**: `frontend` (nếu cần)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Cách 2: Deploy qua Vercel CLI
```bash
npm i -g vercel
vercel login
vercel
```

## Bước 4: Cấu hình Environment Variables

Trong Vercel Dashboard > Project Settings > Environment Variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `https://your-backend-url.com` | URL của backend API |
| `VITE_DEV_MODE` | `false` | Chế độ production |

## Bước 5: Kiểm tra deployment

Sau khi deploy thành công:
- URL: `https://your-project.vercel.app`
- Kiểm tra console để đảm bảo không có lỗi
- Test các tính năng chính của ứng dụng

## 🔧 Troubleshooting

### Lỗi build
```bash
npm run lint
npm run build
```

### Lỗi API connection
- Kiểm tra `VITE_API_URL` trong Vercel environment variables
- Đảm bảo backend đang hoạt động
- Kiểm tra CORS configuration trên backend

### Lỗi routing
- Kiểm tra file `vercel.json`
- Đảm bảo có rewrite rule cho SPA

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra Vercel build logs
2. Xem console errors trong browser
3. Kiểm tra Network tab để debug API calls
