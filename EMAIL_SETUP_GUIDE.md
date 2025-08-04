# 📧 Hướng Dẫn Setup Email Chi Tiết

## 🎯 Tổng Quan
Hướng dẫn này sẽ giúp bạn thiết lập hệ thống gửi email cho EmbeddedChat để có thể gửi workflow reports qua email.

## ✅ Yêu Cầu
- Gmail, Outlook, hoặc Yahoo account
- 2-Step Verification đã được bật
- Quyền truy cập vào Google Account Settings

---

## 🔧 BƯỚC 1: Cấu Hình File .env

### 1.1 Mở file `backend/.env`
```bash
# Mở file này bằng VS Code hoặc text editor
backend/.env
```

### 1.2 Thêm cấu hình email vào cuối file:
```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=EmbeddedChat System
```

⚠️ **LƯU Ý**: Thay `your-email@gmail.com` và `your-app-password` bằng thông tin thực của bạn.

---

## 📧 BƯỚC 2: Tạo Gmail App Password

### 2.1 Truy cập Google Account
1. Đăng nhập vào Gmail
2. Vào [Google Account Settings](https://myaccount.google.com/)
3. Chọn **Security** từ menu bên trái

### 2.2 Bật 2-Step Verification (nếu chưa có)
1. Tìm mục **2-Step Verification**
2. Nhấn **Get started** và làm theo hướng dẫn
3. Xác minh số điện thoại

### 2.3 Tạo App Password
1. Sau khi đã bật 2-Step Verification
2. Quay lại **Security** → **2-Step Verification**
3. Cuộn xuống tìm **App passwords**
4. Nhấn **App passwords**
5. Chọn **Mail** từ dropdown đầu tiên
6. Chọn **Other (Custom name)** từ dropdown thứ hai
7. Nhập tên: `EmbeddedChat`
8. Nhấn **GENERATE**
9. **Copy** mật khẩu 16 ký tự (vd: `abcd efgh ijkl mnop`)

### 2.4 Cập nhật file .env
```env
# Thay your-app-password bằng mật khẩu vừa tạo
SMTP_PASSWORD=abcd efgh ijkl mnop
```

---

## 🔐 BƯỚC 3: Cấu Hình Cho Email Provider Khác

### Gmail (Recommended)
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

### Yahoo
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

---

## 🧪 BƯỚC 4: Kiểm Tra Cấu Hình

### 4.1 Test cấu hình email
```bash
cd backend
python -c "
import sys, os
sys.path.append('src')
from core.email_config import email_settings
print('✅ Config loaded successfully!')
print(f'SMTP: {email_settings.smtp_server}:{email_settings.smtp_port}')
print(f'From: {email_settings.smtp_from_email}')
print(f'Valid: {email_settings.validate_config()}')
"
```

### 4.2 Kết quả mong đợi:
```
✅ Config loaded successfully!
SMTP: smtp.gmail.com:587
From: your-email@gmail.com
Valid: True
```

---

## 🚀 BƯỚC 5: Khởi Động Hệ Thống

### 5.1 Khởi động Backend
```bash
cd backend
python -m uvicorn src.main:app --reload
```

### 5.2 Khởi động Frontend (Terminal mới)
```bash
cd frontend
npm start
```

### 5.3 Truy cập ứng dụng
- Mở browser: `http://localhost:3000`
- Vào **Workflow Editor**
- Tìm **Email Report Panel**

---

## 🎯 BƯỚC 6: Sử Dụng Email Report

### 6.1 Gửi qua UI
1. Vào Workflow Editor
2. Nhấn nút **"Send Email Report"**
3. Chọn loại report (Execution hoặc Daily Analytics)
4. Nhập email người nhận
5. Nhấn **Send**

### 6.2 Gửi qua API
```bash
# Test API endpoint
curl -X POST http://localhost:8000/api/v1/workflow/send-execution-report \
     -H "Content-Type: application/json" \
     -d '{
       "workflow_id": "test-workflow",
       "recipient_email": "your-email@gmail.com",
       "include_analytics": true,
       "include_logs": true
     }'
```

---

## ❌ TROUBLESHOOTING

### Lỗi Authentication Failed
**Nguyên nhân**: App Password không đúng
**Giải pháp**:
- Kiểm tra lại App Password đã copy đúng chưa
- Tạo lại App Password mới
- Đảm bảo 2-Step Verification đã bật

### Lỗi Connection Timeout  
**Nguyên nhân**: Firewall hoặc network block
**Giải pháp**:
- Kiểm tra firewall có block port 587 không
- Thử đổi sang port 465:
  ```env
  SMTP_PORT=465
  SMTP_USE_TLS=false
  SMTP_USE_SSL=true
  ```
- Tắt VPN nếu đang sử dụng

### Lỗi TLS Handshake Failed
**Nguyên nhân**: Cấu hình TLS/SSL không đúng
**Giải pháp**:
- Với Gmail thử cấu hình này:
  ```env
  SMTP_PORT=465
  SMTP_USE_TLS=false
  SMTP_USE_SSL=true
  ```

### Lỗi Invalid Recipient
**Nguyên nhân**: Format email không đúng
**Giải pháp**:
- Kiểm tra email có đúng format không
- Thử gửi đến email khác

---

## 📝 Ví Dụ File .env Hoàn Chỉnh

```env
# Application
APP_NAME=EmbeddedChat API
VERSION=1.0.0
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# Email Configuration  
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=myemail@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_FROM_EMAIL=myemail@gmail.com
SMTP_FROM_NAME=EmbeddedChat System

# Other configs...
```

---

## 🎉 Hoàn Tất!

Sau khi setup thành công, bạn có thể:

✅ **Gửi Execution Reports**: Báo cáo chi tiết về workflow execution  
✅ **Gửi Daily Analytics**: Báo cáo thống kê hàng ngày với charts  
✅ **Sử dụng qua UI**: Giao diện thân thiện trong Workflow Editor  
✅ **Sử dụng qua API**: Tích hợp vào automation scripts  

---

## 📚 Tài Liệu Tham Khảo

- **API Documentation**: `EMAIL_REPORT_SERVICE_README.md`
- **Implementation Details**: `EMAIL_REPORT_IMPLEMENTATION_SUMMARY.md`
- **Test Scripts**: `test_email_report_service.py`, `demo_email_report_system.py`

---

## 🆘 Cần Hỗ Trợ?

Nếu gặp vấn đề, hãy kiểm tra:

1. **File .env** có đúng format không
2. **App Password** có copy đúng không  
3. **2-Step Verification** đã bật chưa
4. **Firewall/Antivirus** có block không
5. **Network connection** có ổn định không

Good luck! 🚀
