"""
Simple Email Test - Gmail with SSL
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment
load_dotenv("backend/.env")

async def test_gmail_ssl():
    """Test Gmail with SSL configuration"""
    print("🧪 TESTING GMAIL WITH SSL...")
    print("=" * 50)
    
    # Get config from .env
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("SMTP_FROM_EMAIL")
    from_name = os.getenv("SMTP_FROM_NAME")
    
    print(f"Server: {smtp_server}:{smtp_port}")
    print(f"Username: {username}")
    print(f"From: {from_name} <{from_email}>")
    print()
    
    try:
        # Test with SSL on port 465
        print("🔐 Testing with SSL (port 465)...")
        
        smtp = aiosmtplib.SMTP(
            hostname=smtp_server,
            port=smtp_port,
            use_tls=False,  # Don't use STARTTLS
            timeout=30
        )
        
        print("Connecting...")
        await smtp.connect()
        print("✅ Connected!")
        
        print("Authenticating...")
        await smtp.login(username, password)
        print("✅ Authenticated!")
        
        # Send test email
        print("📤 Sending test email...")
        
        message = MIMEMultipart()
        message["Subject"] = "🧪 Test Email - EmbeddedChat SSL"
        message["From"] = f"{from_name} <{from_email}>"
        message["To"] = username  # Send to self
        
        body = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: green;">✅ SSL Email Test Successful!</h2>
            <p>Your Gmail configuration is working correctly with SSL.</p>
            <ul>
                <li><strong>Server:</strong> smtp.gmail.com:465</li>
                <li><strong>Method:</strong> SSL</li>
                <li><strong>Account:</strong> {username}</li>
            </ul>
            <p><em>EmbeddedChat Email Service is ready! 🚀</em></p>
        </body>
        </html>
        """.format(username=username)
        
        message.attach(MIMEText(body, "html"))
        
        await smtp.send_message(message)
        print("✅ Test email sent successfully!")
        
        await smtp.quit()
        print("✅ Connection closed!")
        
        return True
        
    except Exception as e:
        print(f"❌ SSL test failed: {str(e)}")
        
        # Try with STARTTLS on port 587
        print("\n🔄 Trying STARTTLS (port 587)...")
        try:
            smtp = aiosmtplib.SMTP(
                hostname=smtp_server,
                port=587,
                use_tls=True,
                timeout=30
            )
            
            await smtp.connect()
            print("✅ STARTTLS Connected!")
            
            await smtp.login(username, password)
            print("✅ STARTTLS Authenticated!")
            
            await smtp.quit()
            print("✅ STARTTLS works! Consider using port 587 with TLS=true")
            
            return True
            
        except Exception as e2:
            print(f"❌ STARTTLS also failed: {str(e2)}")
            print("\n🛠️  Troubleshooting:")
            print("1. Check if App Password is correct")
            print("2. Ensure 2-Step Verification is enabled")
            print("3. Try generating new App Password")
            print("4. Check firewall/VPN settings")
            return False

async def main():
    """Main test function"""
    print("📧 GMAIL EMAIL SERVICE TEST")
    print("=" * 50)
    
    success = await test_gmail_ssl()
    
    if success:
        print("\n🎉 EMAIL SERVICE READY!")
        print("✅ You can now use the Email Report feature")
        print("\n🚀 Next steps:")
        print("1. cd backend && python -m uvicorn src.main:app --reload")
        print("2. cd frontend && npm start")
        print("3. Test Email Report Panel in UI")
    else:
        print("\n❌ Email setup needs attention")
        print("Please check the troubleshooting steps above")

if __name__ == "__main__":
    asyncio.run(main())
