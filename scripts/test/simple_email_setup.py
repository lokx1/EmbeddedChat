"""
Simple Email Setup Guide
"""
import os


def print_email_setup_guide():
    """Print comprehensive email setup guide"""
    print("=" * 70)
    print("📧 HƯỚNG DẪN SETUP EMAIL - EmbeddedChat")
    print("=" * 70)
    print()
    
    print("🔧 BƯỚC 1: Cấu hình file .env")
    print("-" * 50)
    print("Mở file backend/.env và thêm các dòng sau:")
    print()
    print("# Email Configuration")
    print("SMTP_SERVER=smtp.gmail.com")
    print("SMTP_PORT=587")
    print("SMTP_USE_TLS=true")
    print("SMTP_USERNAME=your-email@gmail.com")
    print("SMTP_PASSWORD=your-app-password")
    print("SMTP_FROM_EMAIL=your-email@gmail.com")
    print("SMTP_FROM_NAME=EmbeddedChat System")
    print()
    
    print("📧 BƯỚC 2: Thiết lập Gmail App Password")
    print("-" * 50)
    print("1. Đăng nhập Gmail → Google Account Settings")
    print("2. Security → 2-Step Verification (bật nếu chưa có)")
    print("3. App passwords → Generate new password")
    print("4. Chọn 'Mail' và 'Other (Custom name)'")
    print("5. Nhập tên: 'EmbeddedChat'")
    print("6. Copy password 16 ký tự và paste vào SMTP_PASSWORD")
    print()
    
    print("🔐 BƯỚC 3: Các email provider khác")
    print("-" * 50)
    
    providers = {
        "Gmail": {
            "server": "smtp.gmail.com",
            "port": "587",
            "tls": "true",
            "note": "Cần App Password"
        },
        "Outlook/Hotmail": {
            "server": "smtp-mail.outlook.com", 
            "port": "587",
            "tls": "true",
            "note": "Cần App Password"
        },
        "Yahoo": {
            "server": "smtp.mail.yahoo.com",
            "port": "587", 
            "tls": "true",
            "note": "Cần App Password"
        }
    }
    
    for name, config in providers.items():
        print(f"{name}:")
        print(f"  SMTP_SERVER={config['server']}")
        print(f"  SMTP_PORT={config['port']}")
        print(f"  SMTP_USE_TLS={config['tls']}")
        print(f"  💡 {config['note']}")
        print()
    
    print("⚠️  LƯU Ý QUAN TRỌNG")
    print("-" * 50)
    print("✅ SỬ DỤNG App Password (KHÔNG phải mật khẩu chính)")
    print("✅ Bật 2-Step Verification")
    print("✅ Không commit file .env vào git")
    print("✅ Kiểm tra firewall có chặn port 587 không")
    print("✅ Thử cổng 465 nếu 587 không hoạt động")
    print()
    
    print("🧪 BƯỚC 4: Kiểm tra cấu hình")
    print("-" * 50)
    print("Sau khi cập nhật .env, chạy lệnh sau để test:")
    print()
    print("cd backend")
    print("python -c \"")
    print("import sys, os")
    print("sys.path.append('src')")
    print("from core.email_config import email_settings")
    print("print('✅ Config loaded successfully!')")
    print("print(f'SMTP: {email_settings.smtp_server}:{email_settings.smtp_port}')")
    print("print(f'From: {email_settings.smtp_from_email}')")
    print("print(f'Valid: {email_settings.validate_config()}')")
    print("\"")
    print()
    
    print("🚀 BƯỚC 5: Khởi động hệ thống")
    print("-" * 50)
    print("1. Khởi động Backend:")
    print("   cd backend")
    print("   python -m uvicorn src.main:app --reload")
    print()
    print("2. Khởi động Frontend:")
    print("   cd frontend") 
    print("   npm start")
    print()
    print("3. Truy cập: http://localhost:3000")
    print("4. Vào Workflow Editor → Email Report Panel")
    print()
    
    print("🎯 BƯỚC 6: Sử dụng Email Report")
    print("-" * 50)
    print("• Trong UI: Nhấn nút 'Send Email Report'")
    print("• Via API: POST /api/v1/workflow/send-execution-report")
    print("• Test API với curl:")
    print("  curl -X POST http://localhost:8000/api/v1/workflow/send-execution-report \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -d '{\"workflow_id\":\"test\",\"recipient_email\":\"your@email.com\"}'")
    print()
    
    print("❌ TROUBLESHOOTING")
    print("-" * 50)
    print("Lỗi thường gặp:")
    print("• 'Authentication failed' → Kiểm tra App Password")
    print("• 'Connection timeout' → Kiểm tra firewall/VPN")
    print("• 'TLS error' → Thử đổi port 587 → 465")
    print("• 'Invalid recipient' → Kiểm tra email format")
    print()
    
    print("🎉 HOÀN TẤT!")
    print("-" * 50)
    print("Bây giờ bạn có thể gửi workflow reports qua email!")
    print("📖 Xem thêm: EMAIL_REPORT_SERVICE_README.md")
    print("=" * 70)


def check_env_file():
    """Check if .env file exists and has email config"""
    env_path = os.path.join("backend", ".env")
    
    if not os.path.exists(env_path):
        print(f"❌ File {env_path} không tồn tại!")
        return False
    
    print(f"✅ File {env_path} đã tồn tại")
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    email_keys = [
        "SMTP_SERVER", "SMTP_PORT", "SMTP_USERNAME", 
        "SMTP_PASSWORD", "SMTP_FROM_EMAIL"
    ]
    
    missing_keys = []
    for key in email_keys:
        if key not in content:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Thiếu các cấu hình: {', '.join(missing_keys)}")
        return False
    
    print("✅ Đã có cấu hình email trong .env")
    return True


if __name__ == "__main__":
    print_email_setup_guide()
    print()
    print("🔍 KIỂM TRA FILE CẤU HÌNH:")
    check_env_file()
