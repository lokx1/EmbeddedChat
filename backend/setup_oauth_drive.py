#!/usr/bin/env python3
"""
Google Drive OAuth Setup Tool
Generate user OAuth credentials instead of service account
"""
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# OAuth 2.0 scopes for Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]

def setup_oauth_credentials():
    """Setup OAuth credentials for Google Drive"""
    
    print("=== Google Drive OAuth Setup ===")
    
    # Path to credentials
    token_file = os.path.join(os.path.dirname(__file__), 'src', 'google_drive_token.json')
    credentials_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
    
    if not os.path.exists(credentials_file):
        print(f"❌ Không tìm thấy credentials.json tại: {credentials_file}")
        print("Hãy tải OAuth 2.0 Client IDs từ Google Console:")
        print("1. Vào https://console.cloud.google.com/")
        print("2. Chọn project của bạn")  
        print("3. APIs & Services > Credentials")
        print("4. Create Credentials > OAuth 2.0 Client IDs")
        print("5. Application type: Desktop application")
        print("6. Download JSON và save as 'credentials.json'")
        return False
    
    creds = None
    # Token file stores the user's access and refresh tokens
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth flow...")
            print("Trình duyệt sẽ mở để bạn đăng nhập Google...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ Credentials saved to: {token_file}")
    
    # Test the credentials
    try:
        service = build('drive', 'v3', credentials=creds)
        
        # Test by listing files
        results = service.files().list(pageSize=1).execute()
        print("✅ OAuth credentials hoạt động!")
        print(f"User có quyền truy cập Google Drive")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test credentials: {str(e)}")
        return False

def test_oauth_upload():
    """Test upload file using OAuth credentials"""
    
    print("\n=== Test OAuth Upload ===")
    
    token_file = os.path.join(os.path.dirname(__file__), 'src', 'google_drive_token.json')
    
    if not os.path.exists(token_file):
        print("❌ Chưa có OAuth token. Chạy setup trước!")
        return False
    
    try:
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        service = build('drive', 'v3', credentials=creds)
        
        # Create test file content
        test_content = json.dumps({
            "test": "OAuth upload test",
            "timestamp": "2025-08-03T11:00:00Z",
            "data": ["item1", "item2", "item3"]
        }, indent=2)
        
        # File metadata
        file_metadata = {
            'name': f'OAuth_Test_{int(time.time())}.json',
            'parents': ['14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182']  # Your folder ID
        }
        
        # Upload file
        from googleapiclient.http import MediaInMemoryUpload
        import time
        
        media = MediaInMemoryUpload(
            test_content.encode('utf-8'),
            mimetype='application/json'
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,size,webViewLink'
        ).execute()
        
        print("🎉 Upload thành công!")
        print(f"📄 File ID: {file.get('id')}")
        print(f"📁 File name: {file.get('name')}")
        print(f"📊 File size: {file.get('size')} bytes")
        print(f"🔗 Link: {file.get('webViewLink')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return False

if __name__ == "__main__":
    import time
    
    print("Google Drive OAuth Fix Tool")
    print("Giải pháp cho lỗi 'Service Accounts do not have storage quota'")
    print("=" * 60)
    
    # Step 1: Setup OAuth
    if setup_oauth_credentials():
        print("\n" + "=" * 60)
        
        # Step 2: Test upload
        test_oauth_upload()
        
        print("\n" + "=" * 60)
        print("🎯 Tiếp theo:")
        print("1. Cập nhật GoogleDriveService để dùng OAuth")
        print("2. Test với component thực")
        print("3. Deploy production")
    else:
        print("\n❌ OAuth setup failed. Kiểm tra lại credentials.json")
