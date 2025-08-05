"""
Email Setup Script
Hướng dẫn và kiểm tra cấu hình email
"""
import os
import sys
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from typing import Dict, Any

# Add backend src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "src"))

from core.email_config import email_settings


class EmailSetupGuide:
    """Guide for setting up email configuration"""
    
    def __init__(self):
        self.config = email_settings
    
    def print_setup_guide(self):
        """Print detailed setup guide"""
        print("=" * 60)
        print("📧 EMAIL SETUP GUIDE - EmbeddedChat")
        print("=" * 60)
        print()
        
        print("🔧 BƯỚC 1: Cấu hình .env file")
        print("-" * 40)
        print("Cập nhật file backend/.env với các thông tin sau:")
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
        print("-" * 40)
        print("1. Đăng nhập vào Gmail account của bạn")
        print("2. Vào Google Account Settings")
        print("3. Security > 2-Step Verification")
        print("4. App passwords > Generate password")
        print("5. Chọn 'Mail' và 'Other' (Custom name)")
        print("6. Copy password và paste vào SMTP_PASSWORD")
        print()
        
        print("🔐 BƯỚC 3: Các nhà cung cấp email khác")
        print("-" * 40)
        print("Gmail:")
        print("  SMTP_SERVER=smtp.gmail.com")
        print("  SMTP_PORT=587")
        print("  SMTP_USE_TLS=true")
        print()
        print("Outlook/Hotmail:")
        print("  SMTP_SERVER=smtp-mail.outlook.com")
        print("  SMTP_PORT=587")
        print("  SMTP_USE_TLS=true")
        print()
        print("Yahoo:")
        print("  SMTP_SERVER=smtp.mail.yahoo.com")
        print("  SMTP_PORT=587")
        print("  SMTP_USE_TLS=true")
        print()
        
        print("⚠️  LƯU Ý BẢO MẬT")
        print("-" * 40)
        print("- Không commit file .env vào git")
        print("- Sử dụng App Password thay vì password chính")
        print("- Bật 2-Step Verification")
        print("- Kiểm tra firewall/antivirus")
        print()
    
    def check_current_config(self):
        """Check current email configuration"""
        print("🔍 KIỂM TRA CẤU HÌNH HIỆN TẠI")
        print("-" * 40)
        
        config_status = {
            "SMTP Server": self.config.smtp_server,
            "SMTP Port": self.config.smtp_port,
            "Use TLS": self.config.smtp_use_tls,
            "Username": self.config.smtp_username,
            "Password": "***" if self.config.smtp_password else "❌ CHƯA CẤU HÌNH",
            "From Email": self.config.smtp_from_email,
            "From Name": self.config.smtp_from_name
        }
        
        for key, value in config_status.items():
            status = "✅" if value and value != "❌ CHƯA CẤU HÌNH" else "❌"
            print(f"{status} {key}: {value}")
        
        print()
        is_valid = self.config.validate_config()
        if is_valid:
            print("✅ Cấu hình email hợp lệ!")
        else:
            print("❌ Cấu hình email chưa đầy đủ!")
        
        return is_valid
    
    async def test_smtp_connection(self):
        """Test SMTP connection"""
        print("🧪 KIỂM TRA KẾT NỐI SMTP")
        print("-" * 40)
        
        try:
            smtp_config = self.config.get_smtp_config()
            
            print(f"Kết nối tới {smtp_config['hostname']}:{smtp_config['port']}...")
            
            smtp = aiosmtplib.SMTP(
                hostname=smtp_config['hostname'],
                port=smtp_config['port'],
                use_tls=smtp_config['use_tls'],
                timeout=smtp_config['timeout']
            )
            
            await smtp.connect()
            print("✅ Kết nối SMTP thành công!")
            
            await smtp.login(
                smtp_config['username'],
                smtp_config['password']
            )
            print("✅ Xác thực SMTP thành công!")
            
            await smtp.quit()
            print("✅ Ngắt kết nối SMTP thành công!")
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi kết nối SMTP: {str(e)}")
            print("\n🛠️  CÁCH KHẮC PHỤC:")
            print("1. Kiểm tra username/password")
            print("2. Kiểm tra App Password (Gmail)")
            print("3. Kiểm tra firewall/antivirus")
            print("4. Thử cổng khác (465 cho SSL)")
            return False
    
    async def send_test_email(self, to_email: str):
        """Send test email"""
        print(f"📤 GỬI EMAIL KIỂM TRA TỚI: {to_email}")
        print("-" * 40)
        
        try:
            # Create test email
            message = MIMEMultipart("alternative")
            message["Subject"] = "🧪 Test Email - EmbeddedChat Setup"
            message["From"] = f"{self.config.smtp_from_name} <{self.config.smtp_from_email}>"
            message["To"] = to_email
            
            # HTML content
            html_content = """
            <html>
                <body style="font-family: Arial, sans-serif; margin: 20px;">
                    <h2 style="color: #2e7d32;">✅ Email Setup Successful!</h2>
                    <p>Chúc mừng! Cấu hình email của bạn đã hoạt động chính xác.</p>
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h3>📊 Thông tin hệ thống:</h3>
                        <ul>
                            <li><strong>Service:</strong> EmbeddedChat Email Report</li>
                            <li><strong>SMTP Server:</strong> {smtp_server}</li>
                            <li><strong>From:</strong> {from_email}</li>
                            <li><strong>Time:</strong> {timestamp}</li>
                        </ul>
                    </div>
                    <p><em>Bây giờ bạn có thể sử dụng Email Report Service để gửi báo cáo workflow!</em></p>
                </body>
            </html>
            """.format(
                smtp_server=self.config.smtp_server,
                from_email=self.config.smtp_from_email,
                timestamp=asyncio.get_event_loop().time()
            )
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            smtp_config = self.config.get_smtp_config()
            
            await aiosmtplib.send(
                message,
                hostname=smtp_config['hostname'],
                port=smtp_config['port'],
                use_tls=smtp_config['use_tls'],
                username=smtp_config['username'],
                password=smtp_config['password'],
                timeout=smtp_config['timeout']
            )
            
            print("✅ Gửi email kiểm tra thành công!")
            print(f"📧 Kiểm tra hộp thư: {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi gửi email: {str(e)}")
            return False


async def main():
    """Main setup function"""
    setup_guide = EmailSetupGuide()
    
    # Print setup guide
    setup_guide.print_setup_guide()
    
    # Check current config
    is_valid = setup_guide.check_current_config()
    
    if not is_valid:
        print("\n⚠️  Vui lòng cấu hình email trong file .env trước khi tiếp tục!")
        return
    
    # Test SMTP connection
    print()
    connection_ok = await setup_guide.test_smtp_connection()
    
    if not connection_ok:
        return
    
    # Ask for test email
    print()
    test_email = input("📧 Nhập email để gửi thử (Enter để bỏ qua): ").strip()
    
    if test_email:
        await setup_guide.send_test_email(test_email)
    
    print()
    print("🎉 SETUP HOÀN TẤT!")
    print("-" * 40)
    print("Bây giờ bạn có thể:")
    print("1. Khởi động backend: cd backend && python -m uvicorn src.main:app --reload")
    print("2. Khởi động frontend: cd frontend && npm start")
    print("3. Sử dụng Email Report Panel trong UI")
    print("4. Gọi API endpoints để gửi báo cáo")


if __name__ == "__main__":
    asyncio.run(main())
