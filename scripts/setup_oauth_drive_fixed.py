#!/usr/bin/env python3
"""
Setup OAuth Drive với file oauth_credentials.json
"""
import os
import json
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

# OAuth 2.0 scopes for Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]

def setup_oauth_credentials():
    """Setup OAuth credentials using oauth_credentials.json"""
    
    print("=== Google Drive OAuth Setup (Fixed) ===")
    
    # Path to OAuth credentials
    token_file = os.path.join(os.path.dirname(__file__), 'src', 'google_drive_token.json')
    oauth_credentials_file = os.path.join(os.path.dirname(__file__), 'oauth_credentials.json')
    
    if not os.path.exists(oauth_credentials_file):
        print(f"❌ Không tìm thấy oauth_credentials.json tại: {oauth_credentials_file}")
        print("\n📋 Hướng dẫn tạo OAuth credentials:")
        print("1. Vào https://console.cloud.google.com/apis/credentials")
        print("2. CREATE CREDENTIALS > OAuth 2.0 Client IDs")
        print("3. Application type: Desktop application")
        print("4. Download JSON và save as 'oauth_credentials.json'")
        return False
    
    creds = None
    
    # Load existing token if available
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            print("📁 Found existing token file")
        except Exception as e:
            print(f"⚠️ Error loading existing token: {e}")
            creds = None
    
    # Check if credentials need refresh or new authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired credentials...")
            try:
                creds.refresh(Request())
                print("✅ Credentials refreshed successfully")
            except Exception as e:
                print(f"❌ Failed to refresh credentials: {e}")
                creds = None
        
        if not creds:
            print("🔐 Starting OAuth authorization flow...")
            print("📱 Browser sẽ mở để bạn đăng nhập Google account...")
            print("👤 Đăng nhập với account: long.luubaodepzai8@hcmut.edu.vn")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(oauth_credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
                print("✅ OAuth authorization completed!")
            except Exception as e:
                print(f"❌ OAuth flow failed: {e}")
                return False
        
        # Save credentials for future use
        try:
            # Ensure src directory exists
            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            print(f"💾 Credentials saved to: {token_file}")
        except Exception as e:
            print(f"⚠️ Warning: Could not save credentials: {e}")
    
    # Test the credentials
    try:
        service = build('drive', 'v3', credentials=creds)
        
        # Test by getting user info
        about = service.about().get(fields="user").execute()
        user_email = about.get('user', {}).get('emailAddress', 'Unknown')
        
        print(f"✅ OAuth credentials working!")
        print(f"👤 Authenticated as: {user_email}")
        print(f"🔑 Token type: User OAuth (not service account)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing credentials: {str(e)}")
        return False

def test_oauth_upload():
    """Test upload file using OAuth credentials"""
    
    print("\n=== Test OAuth Upload ===")
    
    token_file = os.path.join(os.path.dirname(__file__), 'src', 'google_drive_token.json')
    
    if not os.path.exists(token_file):
        print("❌ No OAuth token found. Run setup first!")
        return False
    
    try:
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("❌ Invalid credentials. Run setup again.")
                return False
        
        service = build('drive', 'v3', credentials=creds)
        
        # Create test file content
        test_data = {
            "test": "OAuth upload test - FIXED!",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": [
                {"name": "Test User 1", "email": "test1@example.com"},
                {"name": "Test User 2", "email": "test2@example.com"}
            ],
            "metadata": {
                "upload_method": "OAuth 2.0",
                "account_type": "User Account",
                "quota_unlimited": True
            }
        }
        
        test_content = json.dumps(test_data, indent=2, ensure_ascii=False)
        
        # File metadata
        timestamp = int(time.time())
        file_metadata = {
            'name': f'OAuth_Test_SUCCESS_{timestamp}.json',
            'parents': ['14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182']  # Your folder ID
        }
        
        print(f"📁 Uploading to folder: 14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182")
        print(f"📄 File name: {file_metadata['name']}")
        
        # Upload file
        media = MediaInMemoryUpload(
            test_content.encode('utf-8'),
            mimetype='application/json'
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,size,webViewLink,createdTime'
        ).execute()
        
        print("\n🎉 UPLOAD THÀNH CÔNG!")
        print("=" * 50)
        print(f"📄 File ID: {file.get('id')}")
        print(f"📁 File name: {file.get('name')}")
        print(f"📊 File size: {file.get('size')} bytes")
        print(f"⏰ Created: {file.get('createdTime')}")
        print(f"🔗 View link: {file.get('webViewLink')}")
        print("=" * 50)
        
        # Verify in folder
        print(f"\n📂 Checking files in folder...")
        folder_files = service.files().list(
            q=f"'14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182' in parents",
            fields="files(id,name,size,createdTime)"
        ).execute()
        
        files = folder_files.get('files', [])
        print(f"📊 Total files in folder: {len(files)}")
        
        recent_files = sorted(files, key=lambda x: x.get('createdTime', ''), reverse=True)[:3]
        print("📋 Recent files:")
        for f in recent_files:
            print(f"   - {f.get('name')} ({f.get('size')} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        
        # Check specific error types
        if "403" in str(e) and "quota" in str(e).lower():
            print("💡 Still getting quota error? Check:")
            print("   1. Using OAuth credentials (not service account)")
            print("   2. Logged in with correct user account")
            print("   3. Account has Drive storage available")
        
        return False

def show_success_summary():
    """Show success summary and next steps"""
    
    print("\n" + "=" * 70)
    print("🎉 OAUTH SETUP HOÀN THÀNH THÀNH CÔNG!")
    print("=" * 70)
    
    print("\n✅ Đã giải quyết được lỗi:")
    print("   ❌ 'Service Accounts do not have storage quota'")
    print("   ✅ Chuyển sang OAuth User Credentials")
    
    print("\n🔧 Files được tạo:")
    print("   📁 src/google_drive_token.json - OAuth token")
    print("   📊 oauth_credentials.json - OAuth client config")
    
    print("\n🚀 Tiếp theo:")
    print("   1. Test component: python test_simple_drive.py")
    print("   2. Test workflow: python test_complete_workflow.py")
    print("   3. Sử dụng trong frontend workflow")
    
    print("\n💡 Lưu ý:")
    print("   🔄 Token sẽ tự động refresh khi hết hạn")
    print("   👤 Upload với quota của user account")
    print("   🔒 Secure hơn service account cho production")

if __name__ == "__main__":
    print("🔧 Google Drive OAuth Setup Tool - FIXED VERSION")
    print("Giải pháp cho lỗi 'Service Accounts do not have storage quota'")
    print("=" * 70)
    
    # Step 1: Setup OAuth credentials
    if setup_oauth_credentials():
        print("\n" + "=" * 70)
        
        # Step 2: Test upload
        if test_oauth_upload():
            show_success_summary()
        else:
            print("\n❌ Upload test failed, but OAuth setup is complete")
            print("💡 Có thể test lại sau với: python test_oauth_upload.py")
    else:
        print("\n❌ OAuth setup failed")
        print("📋 Kiểm tra lại oauth_credentials.json")
        print("🔗 Hướng dẫn: python oauth_setup_guide.py")
