# Script tự động deploy lên Railway
# Chạy script này từ thư mục backend

Write-Host "🚀 Bắt đầu deploy Backend lên Railway..." -ForegroundColor Green

# Kiểm tra Railway CLI
Write-Host "📋 Kiểm tra Railway CLI..." -ForegroundColor Yellow
try {
    $railwayVersion = railway --version
    Write-Host "✅ Railway CLI đã được cài đặt: $railwayVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Railway CLI chưa được cài đặt. Vui lòng cài đặt trước:" -ForegroundColor Red
    Write-Host "npm install -g @railway/cli" -ForegroundColor Cyan
    exit 1
}

# Kiểm tra đăng nhập
Write-Host "🔐 Kiểm tra đăng nhập Railway..." -ForegroundColor Yellow
try {
    $user = railway whoami
    Write-Host "✅ Đã đăng nhập với: $user" -ForegroundColor Green
} catch {
    Write-Host "❌ Chưa đăng nhập Railway. Vui lòng đăng nhập:" -ForegroundColor Red
    Write-Host "railway login" -ForegroundColor Cyan
    exit 1
}

# Kiểm tra project
Write-Host "📁 Kiểm tra project Railway..." -ForegroundColor Yellow
try {
    $project = railway status
    Write-Host "✅ Đã kết nối với project Railway" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Chưa kết nối với project Railway. Tạo project mới..." -ForegroundColor Yellow
    railway init
}

# Deploy
Write-Host "🚀 Bắt đầu deploy..." -ForegroundColor Green
railway up

Write-Host "✅ Deploy hoàn tất!" -ForegroundColor Green
Write-Host "🌐 URL của ứng dụng sẽ được hiển thị ở trên" -ForegroundColor Cyan
Write-Host "📊 Xem logs: railway logs" -ForegroundColor Cyan
Write-Host "🔧 Xem status: railway status" -ForegroundColor Cyan
