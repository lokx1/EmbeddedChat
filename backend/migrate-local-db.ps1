# Script migrate database từ local PostgreSQL sang Railway
# Chạy script này từ thư mục backend

Write-Host "🚀 Migration từ Local PostgreSQL sang Railway" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

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

# Kiểm tra đăng nhập Railway
Write-Host "🔐 Kiểm tra đăng nhập Railway..." -ForegroundColor Yellow
try {
    $user = railway whoami
    Write-Host "✅ Đã đăng nhập với: $user" -ForegroundColor Green
} catch {
    Write-Host "❌ Chưa đăng nhập Railway. Vui lòng đăng nhập:" -ForegroundColor Red
    Write-Host "railway login" -ForegroundColor Cyan
    exit 1
}

# Lấy thông tin database local
Write-Host "📋 Nhập thông tin PostgreSQL local:" -ForegroundColor Yellow

$host = Read-Host "Host (localhost)" 
if (-not $host) { $host = "localhost" }

$port = Read-Host "Port (5432)"
if (-not $port) { $port = "5432" }

$database = Read-Host "Database name"
if (-not $database) {
    Write-Host "❌ Database name không được để trống" -ForegroundColor Red
    exit 1
}

$username = Read-Host "Username"
if (-not $username) {
    Write-Host "❌ Username không được để trống" -ForegroundColor Red
    exit 1
}

$password = Read-Host "Password" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

# Export database local
Write-Host "🔄 Exporting database local..." -ForegroundColor Yellow

$backupFile = "local_db_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
$env:PGPASSWORD = $passwordPlain

try {
    $pgDumpCmd = "pg_dump -h $host -p $port -U $username -d $database -f $backupFile"
    Invoke-Expression $pgDumpCmd
    
    if (Test-Path $backupFile) {
        Write-Host "✅ Export thành công: $backupFile" -ForegroundColor Green
    } else {
        Write-Host "❌ Export thất bại" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Lỗi khi export: $_" -ForegroundColor Red
    exit 1
}

# Kiểm tra Railway database URL
Write-Host "🔍 Kiểm tra Railway DATABASE_URL..." -ForegroundColor Yellow
try {
    $variables = railway variables
    $dbUrl = $variables | Select-String "DATABASE_URL" | ForEach-Object { $_.ToString().Split('=')[1].Trim() }
    
    if ($dbUrl) {
        Write-Host "✅ Tìm thấy DATABASE_URL: $dbUrl" -ForegroundColor Green
    } else {
        Write-Host "❌ Không tìm thấy DATABASE_URL trong Railway" -ForegroundColor Red
        Write-Host "Vui lòng tạo PostgreSQL service và cấu hình DATABASE_URL trước" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Lỗi khi lấy Railway variables: $_" -ForegroundColor Red
    exit 1
}

# Import vào Railway
Write-Host "🔄 Importing data vào Railway..." -ForegroundColor Yellow
try {
    $importCmd = "railway shell -c 'psql `$DATABASE_URL < $backupFile'"
    Invoke-Expression $importCmd
    Write-Host "✅ Import thành công" -ForegroundColor Green
} catch {
    Write-Host "❌ Lỗi khi import: $_" -ForegroundColor Red
    exit 1
}

# Test kết nối Railway
Write-Host "🔍 Test kết nối Railway database..." -ForegroundColor Yellow
try {
    $testScript = @"
import asyncio
import os
from src.models.database import engine

async def test_db():
    try:
        async with engine.begin() as conn:
            result = await conn.execute('SELECT 1')
            print('✅ Railway database connection successful!')
            return True
    except Exception as e:
        print(f'❌ Railway database connection failed: {e}')
        return False

asyncio.run(test_db())
"@

    $testFile = "test_railway_db.py"
    $testScript | Out-File -FilePath $testFile -Encoding UTF8
    
    python $testFile
    
    if (Test-Path $testFile) {
        Remove-Item $testFile
    }
    
} catch {
    Write-Host "❌ Lỗi khi test kết nối: $_" -ForegroundColor Red
}

# Xóa file backup
if (Test-Path $backupFile) {
    Remove-Item $backupFile
    Write-Host "🗑️ Đã xóa file backup: $backupFile" -ForegroundColor Cyan
}

Write-Host "🎉 Migration hoàn tất!" -ForegroundColor Green
Write-Host "📊 Railway database đã sẵn sàng để sử dụng" -ForegroundColor Cyan
