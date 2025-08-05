"""
Test Email Service - EmbeddedChat
Kiểm tra email service có hoạt động không
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend src to path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path / "src"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_path / ".env")

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailTester:
    """Class to test email configuration and service"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_from_email = os.getenv("SMTP_FROM_EMAIL")
        self.smtp_from_name = os.getenv("SMTP_FROM_NAME")
    
    def print_config(self):
        """Print current email configuration"""
        print("=" * 60)
        print("📧 EMAIL CONFIGURATION")
        print("=" * 60)
        print(f"SMTP Server: {self.smtp_server}")
        print(f"SMTP Port: {self.smtp_port}")
        print(f"Use TLS: {self.smtp_use_tls}")
        print(f"Username: {self.smtp_username}")
        print(f"Password: {'*' * len(self.smtp_password) if self.smtp_password else 'NOT SET'}")
        print(f"From Email: {self.smtp_from_email}")
        print(f"From Name: {self.smtp_from_name}")
        print()
    
    async def test_smtp_connection(self):
        """Test SMTP connection and authentication"""
        print("🔌 TESTING SMTP CONNECTION...")
        print("-" * 40)
        
        try:
            # Create SMTP connection
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_server,
                port=self.smtp_port,
                use_tls=self.smtp_use_tls,
                timeout=30
            )
            
            print(f"Connecting to {self.smtp_server}:{self.smtp_port}...")
            await smtp.connect()
            print("✅ Connection successful!")
            
            print("Authenticating...")
            await smtp.login(self.smtp_username, self.smtp_password)
            print("✅ Authentication successful!")
            
            await smtp.quit()
            print("✅ SMTP test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ SMTP test failed: {str(e)}")
            print("\n🛠️  Possible solutions:")
            print("- Check username/password in .env file")
            print("- Ensure 2-Step Verification is enabled")
            print("- Generate new App Password for Gmail")
            print("- Check firewall/antivirus settings")
            return False
    
    async def send_test_email(self, to_email: str = None):
        """Send a test email"""
        if not to_email:
            to_email = self.smtp_username
        
        print(f"📤 SENDING TEST EMAIL TO: {to_email}")
        print("-" * 40)
        
        try:
            # Create test email
            message = MIMEMultipart("alternative")
            message["Subject"] = "🧪 Test Email - EmbeddedChat System"
            message["From"] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
            message["To"] = to_email
            
            # HTML content
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; margin: 20px;">
                    <h2 style="color: #2e7d32;">✅ Email Service Test Successful!</h2>
                    <p>Chúc mừng! Email service của EmbeddedChat đã hoạt động chính xác.</p>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h3>📊 Configuration Details:</h3>
                        <ul>
                            <li><strong>SMTP Server:</strong> {self.smtp_server}:{self.smtp_port}</li>
                            <li><strong>From Email:</strong> {self.smtp_from_email}</li>
                            <li><strong>From Name:</strong> {self.smtp_from_name}</li>
                            <li><strong>Test Time:</strong> {asyncio.get_event_loop().time()}</li>
                        </ul>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h3>🚀 Next Steps:</h3>
                        <ol>
                            <li>Start backend server: <code>cd backend && python -m uvicorn src.main:app --reload</code></li>
                            <li>Start frontend: <code>cd frontend && npm start</code></li>
                            <li>Use Email Report Panel in Workflow Editor</li>
                            <li>Call API endpoints to send workflow reports</li>
                        </ol>
                    </div>
                    
                    <p><em>Your Email Report Service is ready to use! 🎉</em></p>
                </body>
            </html>
            """
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                use_tls=self.smtp_use_tls,
                username=self.smtp_username,
                password=self.smtp_password,
                timeout=30
            )
            
            print("✅ Test email sent successfully!")
            print(f"📧 Check your inbox: {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send test email: {str(e)}")
            return False
    
    async def test_email_report_service(self):
        """Test the actual EmailReportService"""
        print("🧪 TESTING EMAIL REPORT SERVICE...")
        print("-" * 40)
        
        try:
            from services.workflow.email_report_service import EmailReportService
            
            service = EmailReportService()
            print("✅ EmailReportService imported successfully!")
            
            # Test service configuration
            if hasattr(service, 'validate_email_config'):
                is_valid = service.validate_email_config()
                print(f"Configuration valid: {'✅' if is_valid else '❌'}")
            
            return True
            
        except ImportError as e:
            print(f"❌ Could not import EmailReportService: {str(e)}")
            print("💡 Make sure backend/src/services/workflow/email_report_service.py exists")
            return False
        except Exception as e:
            print(f"❌ Error testing EmailReportService: {str(e)}")
            return False


async def main():
    """Main test function"""
    print("🚀 STARTING EMAIL SERVICE TEST")
    print("=" * 60)
    
    tester = EmailTester()
    
    # Print configuration
    tester.print_config()
    
    # Test SMTP connection
    smtp_ok = await tester.test_smtp_connection()
    print()
    
    if not smtp_ok:
        print("❌ SMTP test failed. Please fix configuration before proceeding.")
        return
    
    # Test EmailReportService
    service_ok = await tester.test_email_report_service()
    print()
    
    # Send test email
    print("📧 Would you like to send a test email? (y/n): ", end="")
    # For automation, send to self
    test_email = tester.smtp_username
    print(f"Sending test email to: {test_email}")
    
    email_ok = await tester.send_test_email(test_email)
    print()
    
    # Final results
    print("=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"{'✅' if smtp_ok else '❌'} SMTP Connection & Authentication")
    print(f"{'✅' if service_ok else '❌'} EmailReportService Import")
    print(f"{'✅' if email_ok else '❌'} Test Email Sending")
    print()
    
    if smtp_ok and service_ok and email_ok:
        print("🎉 ALL TESTS PASSED!")
        print("Your email service is ready to use!")
        print()
        print("🚀 Next steps:")
        print("1. Start backend: cd backend && python -m uvicorn src.main:app --reload")
        print("2. Start frontend: cd frontend && npm start")
        print("3. Use Email Report Panel in UI")
    else:
        print("❌ Some tests failed. Please check the issues above.")


if __name__ == "__main__":
    asyncio.run(main())
