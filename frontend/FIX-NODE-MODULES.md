# 🔧 Hướng dẫn xử lý node_modules

## 🚨 Vấn đề: Đã push nhầm node_modules lên GitHub

### Giải pháp nhanh:

#### Bước 1: Chạy script dọn dẹp

**Windows (PowerShell):**
```powershell
.\clean-and-push.ps1
```

**Linux/Mac:**
```bash
chmod +x clean-and-push.sh
./clean-and-push.sh
```

#### Bước 2: Push lại code
```bash
git add .
git commit -m "Remove node_modules and clean repository"
git push origin BE-FE-DEPLOYMENT
```

#### Bước 3: Cài lại dependencies (sau khi push)
```bash
npm install
```

## 📋 Các file đã được tạo:

1. **`.gitignore`** - Loại trừ node_modules và các file không cần thiết
2. **`clean-and-push.sh`** - Script dọn dẹp cho Linux/Mac
3. **`clean-and-push.ps1`** - Script dọn dẹp cho Windows PowerShell

## ⚠️ Lưu ý quan trọng:

- **KHÔNG BAO GIỜ** push `node_modules/` lên GitHub
- Luôn sử dụng `.gitignore` để loại trừ node_modules
- Vercel sẽ tự động cài đặt dependencies từ `package.json`

## 🔍 Kiểm tra sau khi push:

```bash
# Kiểm tra git status
git status

# Kiểm tra file đã được ignore
git check-ignore node_modules/

# Kiểm tra size của repository
git count-objects -vH
```

## 🚀 Sau khi fix xong:

1. Vercel sẽ tự động trigger build mới
2. Build sẽ thành công vì không còn node_modules
3. Dependencies sẽ được cài đặt tự động trên Vercel

## 💡 Tips:

- Luôn chạy `npm install` sau khi clone repository mới
- Sử dụng `npm ci` trong production để cài đặt chính xác versions
- Kiểm tra `.gitignore` trước khi commit
