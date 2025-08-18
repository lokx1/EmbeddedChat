# Deploy với minimal requirements
Write-Host "🚀 Deploy Backend với Minimal Requirements" -ForegroundColor Green

# Backup current requirements.txt
if (Test-Path "requirements.txt") {
    Copy-Item "requirements.txt" "requirements-full-backup.txt"
    Write-Host "📋 Đã backup requirements.txt thành requirements-full-backup.txt" -ForegroundColor Yellow
}

# Switch to minimal requirements
if (Test-Path "requirements-minimal.txt") {
    Copy-Item "requirements-minimal.txt" "requirements.txt"
    Write-Host "📦 Đã switch sang minimal requirements" -ForegroundColor Green
} else {
    Write-Host "❌ Không tìm thấy requirements-minimal.txt" -ForegroundColor Red
    exit 1
}

# Deploy
Write-Host "🚀 Deploying với minimal requirements..." -ForegroundColor Green
try {
    & ".\deploy-to-railway.ps1"
    Write-Host "✅ Deploy thành công!" -ForegroundColor Green
} catch {
    Write-Host "❌ Deploy thất bại: $_" -ForegroundColor Red
    
    # Restore original requirements
    if (Test-Path "requirements-full-backup.txt") {
        Copy-Item "requirements-full-backup.txt" "requirements.txt"
        Remove-Item "requirements-full-backup.txt"
        Write-Host "🔄 Đã restore requirements.txt gốc" -ForegroundColor Yellow
    }
    exit 1
}

Write-Host "🎉 Deploy hoàn tất với minimal requirements!" -ForegroundColor Green
Write-Host "📌 Lưu ý: requirements.txt hiện tại là minimal version" -ForegroundColor Cyan
Write-Host "📌 Full requirements được backup trong requirements-full-backup.txt" -ForegroundColor Cyan
