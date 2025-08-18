# PowerShell script để dọn dẹp và push lại code

Write-Host "🧹 Bắt đầu dọn dẹp và push lại code..." -ForegroundColor Green

# Xóa node_modules
Write-Host "📦 Xóa node_modules..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

# Xóa các file cache
Write-Host "🗑️  Xóa cache..." -ForegroundColor Yellow
if (Test-Path ".npm") {
    Remove-Item -Recurse -Force ".npm"
}
if (Test-Path ".cache") {
    Remove-Item -Recurse -Force ".cache"
}
if (Test-Path ".parcel-cache") {
    Remove-Item -Recurse -Force ".parcel-cache"
}

# Xóa các file log
Write-Host "📝 Xóa log files..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Filter "*.log" | Remove-Item -Force
Get-ChildItem -Path "." -Filter "npm-debug.log*" | Remove-Item -Force
Get-ChildItem -Path "." -Filter "yarn-debug.log*" | Remove-Item -Force
Get-ChildItem -Path "." -Filter "yarn-error.log*" | Remove-Item -Force

# Xóa các file environment
Write-Host "🔐 Xóa environment files..." -ForegroundColor Yellow
if (Test-Path ".env") { Remove-Item ".env" -Force }
if (Test-Path ".env.local") { Remove-Item ".env.local" -Force }
if (Test-Path ".env.development.local") { Remove-Item ".env.development.local" -Force }
if (Test-Path ".env.test.local") { Remove-Item ".env.test.local" -Force }
if (Test-Path ".env.production.local") { Remove-Item ".env.production.local" -Force }

# Xóa các file OS
Write-Host "💻 Xóa OS files..." -ForegroundColor Yellow
if (Test-Path ".DS_Store") { Remove-Item ".DS_Store" -Force }
if (Test-Path "Thumbs.db") { Remove-Item "Thumbs.db" -Force }

Write-Host "✅ Dọn dẹp hoàn tất!" -ForegroundColor Green

# Kiểm tra git status
Write-Host "📊 Kiểm tra git status..." -ForegroundColor Cyan
git status

Write-Host ""
Write-Host "🚀 Bước tiếp theo:" -ForegroundColor Magenta
Write-Host "1. git add ."
Write-Host "2. git commit -m 'Remove node_modules and clean repository'"
Write-Host "3. git push origin BE-FE-DEPLOYMENT"
Write-Host ""
Write-Host "💡 Sau khi push, bạn có thể chạy: npm install để cài lại dependencies" -ForegroundColor Yellow
