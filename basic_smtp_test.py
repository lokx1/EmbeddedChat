"""
Basic SMTP Test - Standard smtplib
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment
load_dotenv("backend/.env")

def test_basic_smtp():
    """Test with standard smtplib"""
    print("📧 BASIC SMTP TEST")
    print("=" * 40)
    
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("SMTP_FROM_EMAIL")
    from_name = os.getenv("SMTP_FROM_NAME")
    
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password) if password else 'NOT SET'}")
    print()
    
    # Test 1: Gmail with TLS (port 587)
    print("🔐 Test 1: Gmail TLS (port 587)")
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(username, password)
        print("✅ TLS Login successful!")
        
        # Send test email
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = username
        msg['Subject'] = "🧪 EmbeddedChat SMTP Test - TLS"
        
        body = f"""
        ✅ SMTP Test Successful!
        
        Your email configuration is working:
        - Server: smtp.gmail.com:587
        - Method: STARTTLS
        - From: {from_email}
        
        EmbeddedChat Email Service is ready! 🚀
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Test email sent via TLS!")
        return True
        
    except Exception as e:
        print(f"❌ TLS failed: {str(e)}")
    
    # Test 2: Gmail with SSL (port 465)
    print("\n🔐 Test 2: Gmail SSL (port 465)")
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(username, password)
        print("✅ SSL Login successful!")
        
        # Send test email
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = username
        msg['Subject'] = "🧪 EmbeddedChat SMTP Test - SSL"
        
        body = f"""
        ✅ SMTP Test Successful!
        
        Your email configuration is working:
        - Server: smtp.gmail.com:465
        - Method: SSL
        - From: {from_email}
        
        EmbeddedChat Email Service is ready! 🚀
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Test email sent via SSL!")
        return True
        
    except Exception as e:
        print(f"❌ SSL failed: {str(e)}")
    
    return False

def check_app_password():
    """Check App Password format"""
    password = os.getenv("SMTP_PASSWORD", "")
    
    print("🔍 CHECKING APP PASSWORD FORMAT")
    print("=" * 40)
    print(f"Password length: {len(password)}")
    print(f"Has spaces: {' ' in password}")
    print(f"Format: {password[:4]}{'*' * (len(password)-8)}{password[-4:] if len(password) > 8 else ''}")
    
    if len(password) == 16 and ' ' not in password:
        print("✅ App Password format looks correct (16 chars, no spaces)")
    elif len(password) == 19 and password.count(' ') == 3:
        print("⚠️  App Password has spaces - removing spaces...")
        clean_password = password.replace(' ', '')
        print(f"Clean password: {clean_password}")
        return clean_password
    else:
        print("❌ App Password format may be incorrect")
        print("Expected: 16 characters without spaces")
        print("Or: 19 characters with 3 spaces (xxxx xxxx xxxx xxxx)")
    
    return password

def main():
    """Main test function"""
    print("🚀 COMPREHENSIVE EMAIL TEST")
    print("=" * 50)
    
    # Check password format first
    correct_password = check_app_password()
    
    # Update environment if needed
    if correct_password != os.getenv("SMTP_PASSWORD"):
        os.environ["SMTP_PASSWORD"] = correct_password
        print("🔄 Updated password format for testing")
    
    print()
    
    # Test SMTP
    success = test_basic_smtp()
    
    if success:
        print("\n🎉 EMAIL SERVICE TEST PASSED!")
        print("✅ Your email configuration is working correctly")
        print("\n📋 Recommended .env configuration:")
        
        if "TLS" in locals():
            print("SMTP_SERVER=smtp.gmail.com")
            print("SMTP_PORT=587")
            print("SMTP_USE_TLS=true")
        else:
            print("SMTP_SERVER=smtp.gmail.com")
            print("SMTP_PORT=465")
            print("SMTP_USE_TLS=false")
            print("SMTP_USE_SSL=true")
        
        print(f"SMTP_USERNAME={os.getenv('SMTP_USERNAME')}")
        print(f"SMTP_PASSWORD={correct_password}")
        
        print("\n🚀 Ready to use Email Report Service!")
        
    else:
        print("\n❌ EMAIL TEST FAILED")
        print("🛠️  Please check:")
        print("1. App Password is correct (16 characters)")
        print("2. 2-Step Verification is enabled in Gmail")
        print("3. 'Less secure app access' is turned off (use App Password)")
        print("4. Network/firewall allows SMTP connections")
        print("5. Try generating a new App Password")

if __name__ == "__main__":
    main()
