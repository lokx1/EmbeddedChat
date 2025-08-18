# Script test requirements trước khi deploy lên Railway
Write-Host "🧪 Testing Requirements for Railway Deployment" -ForegroundColor Green

# Tạo virtual environment test
Write-Host "📦 Tạo virtual environment test..." -ForegroundColor Yellow
python -m venv test_env

# Activate virtual environment
Write-Host "🔄 Kích hoạt virtual environment..." -ForegroundColor Yellow
& "test_env\Scripts\Activate.ps1"

# Test minimal requirements trước
Write-Host "📋 Testing minimal requirements..." -ForegroundColor Yellow
try {
    pip install -r requirements-minimal.txt
    Write-Host "✅ Minimal requirements OK" -ForegroundColor Green
    $minimalOK = $true
} catch {
    Write-Host "❌ Minimal requirements FAILED: $_" -ForegroundColor Red
    $minimalOK = $false
}

# Test full requirements
Write-Host "📋 Testing full requirements..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✅ Full requirements OK" -ForegroundColor Green
    $fullOK = $true
} catch {
    Write-Host "❌ Full requirements FAILED: $_" -ForegroundColor Red
    $fullOK = $false
}

# Deactivate và cleanup
deactivate
Remove-Item -Recurse -Force test_env

# Recommendations
Write-Host "`n📊 Test Results:" -ForegroundColor Cyan
if ($minimalOK) {
    Write-Host "✅ Minimal requirements: PASSED" -ForegroundColor Green
    Write-Host "💡 Khuyến nghị: Sử dụng requirements-minimal.txt cho Railway" -ForegroundColor Yellow
} else {
    Write-Host "❌ Minimal requirements: FAILED" -ForegroundColor Red
}

if ($fullOK) {
    Write-Host "✅ Full requirements: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Full requirements: FAILED" -ForegroundColor Red
}

Write-Host "`n🚀 Next steps:" -ForegroundColor Cyan
if ($minimalOK) {
    Write-Host "1. Rename requirements.txt to requirements-full.txt" -ForegroundColor White
    Write-Host "2. Rename requirements-minimal.txt to requirements.txt" -ForegroundColor White
    Write-Host "3. Deploy với: .\deploy-to-railway.ps1" -ForegroundColor White
} else {
    Write-Host "1. Sửa dependency conflicts trong requirements" -ForegroundColor White
    Write-Host "2. Chạy lại test này" -ForegroundColor White
}
