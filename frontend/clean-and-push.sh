#!/bin/bash

echo "🧹 Bắt đầu dọn dẹp và push lại code..."

# Xóa node_modules
echo "📦 Xóa node_modules..."
rm -rf node_modules/
rm -rf dist/

# Xóa các file cache
echo "🗑️  Xóa cache..."
rm -rf .npm/
rm -rf .cache/
rm -rf .parcel-cache/

# Xóa các file log
echo "📝 Xóa log files..."
rm -f *.log
rm -f npm-debug.log*
rm -f yarn-debug.log*
rm -f yarn-error.log*

# Xóa các file environment
echo "🔐 Xóa environment files..."
rm -f .env
rm -f .env.local
rm -f .env.development.local
rm -f .env.test.local
rm -f .env.production.local

# Xóa các file OS
echo "💻 Xóa OS files..."
rm -f .DS_Store
rm -f Thumbs.db

echo "✅ Dọn dẹp hoàn tất!"

# Kiểm tra git status
echo "📊 Kiểm tra git status..."
git status

echo ""
echo "🚀 Bước tiếp theo:"
echo "1. git add ."
echo "2. git commit -m 'Remove node_modules and clean repository'"
echo "3. git push origin BE-FE-DEPLOYMENT"
echo ""
echo "💡 Sau khi push, bạn có thể chạy: npm install để cài lại dependencies"
