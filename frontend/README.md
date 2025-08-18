# EmbeddedChat Frontend

Ứng dụng chat AI với giao diện người dùng hiện đại, được xây dựng bằng React, TypeScript và Vite.

## 🚀 Deploy lên Vercel

### Bước 1: Chuẩn bị
1. Đảm bảo bạn có tài khoản GitHub và Vercel
2. Push code lên GitHub repository

### Bước 2: Deploy trên Vercel
1. Truy cập [vercel.com](https://vercel.com)
2. Đăng nhập và click "New Project"
3. Import repository từ GitHub
4. Cấu hình project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend` (nếu repo chứa cả frontend và backend)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Bước 3: Cấu hình Environment Variables
Trong Vercel Dashboard, thêm các biến môi trường:
- `VITE_API_URL`: URL của backend API (ví dụ: `https://your-backend.vercel.app`)

### Bước 4: Deploy
Click "Deploy" và chờ quá trình hoàn tất.

## 🛠️ Development

### Cài đặt dependencies
```bash
npm install
```

### Chạy development server
```bash
npm run dev
```

### Build production
```bash
npm run build
```

## 📁 Cấu trúc dự án
```
frontend/
├── src/
│   ├── components/     # React components
│   ├── services/       # API services
│   ├── contexts/       # React contexts
│   └── utils/          # Utility functions
├── public/             # Static assets
├── dist/               # Build output
└── package.json        # Dependencies
```

## 🔧 Cấu hình

### Environment Variables
- `VITE_API_URL`: URL của backend API
- `VITE_DEV_MODE`: Chế độ development (true/false)

### Vercel Configuration
File `vercel.json` đã được cấu hình sẵn cho:
- SPA routing (React Router)
- Asset caching
- Build optimization

## 🌐 Production Deployment

Sau khi deploy thành công, ứng dụng sẽ có URL dạng:
`https://your-project-name.vercel.app`

### Lưu ý quan trọng:
1. **Backend URL**: Đảm bảo `VITE_API_URL` trỏ đến backend đã được deploy
2. **CORS**: Backend cần cấu hình CORS để cho phép frontend truy cập
3. **HTTPS**: Vercel tự động cung cấp SSL certificate

## 🐛 Troubleshooting

### Lỗi build
- Kiểm tra TypeScript errors: `npm run lint`
- Đảm bảo tất cả dependencies đã được cài đặt

### Lỗi API connection
- Kiểm tra `VITE_API_URL` trong Vercel environment variables
- Đảm bảo backend đang hoạt động và accessible

### Lỗi routing
- Kiểm tra file `vercel.json` có cấu hình rewrite rules đúng không
