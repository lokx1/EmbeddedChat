#!/usr/bin/env python3
"""
Hướng dẫn tạo OAuth Credentials cho Google Drive
"""

def create_oauth_credentials_guide():
    """Hướng dẫn tạo OAuth 2.0 Client ID"""
    
    print("=" * 70)
    print("🔧 HƯỚNG DẪN TẠO OAUTH 2.0 CLIENT CREDENTIALS")
    print("=" * 70)
    
    print("\n📋 Các bước thực hiện:")
    
    print("\n1️⃣ Mở Google Cloud Console:")
    print("   🔗 https://console.cloud.google.com/")
    
    print("\n2️⃣ Chọn project hiện tại:")
    print("   📁 automation-467607 (hoặc project của bạn)")
    
    print("\n3️⃣ Vào APIs & Services > Credentials:")
    print("   🔗 https://console.cloud.google.com/apis/credentials")
    
    print("\n4️⃣ Tạo Credentials mới:")
    print("   ➕ Click 'CREATE CREDENTIALS'")
    print("   📋 Chọn 'OAuth 2.0 Client IDs'")
    
    print("\n5️⃣ Cấu hình OAuth Client:")
    print("   📱 Application type: 'Desktop application'")
    print("   📝 Name: 'EmbeddedChat Drive Access' (hoặc tên tùy ý)")
    
    print("\n6️⃣ Download credentials:")
    print("   💾 Click 'DOWNLOAD JSON'")
    print("   📁 Save file as: 'oauth_credentials.json'")
    print("   📂 Location: D:\\EmbeddedChat\\backend\\")
    
    print("\n7️⃣ Kiểm tra OAuth Consent Screen:")
    print("   ⚙️ Vào 'OAuth consent screen'")
    print("   👤 Add test users (email của bạn)")
    print("   📧 Thêm email: long.luubaodepzai8@hcmut.edu.vn")
    
    print("\n=" * 70)
    print("💡 LƯU Ý QUAN TRỌNG:")
    print("=" * 70)
    
    print("\n🔄 Khác biệt giữa Service Account và OAuth:")
    print("   📊 Service Account: Bot account, có giới hạn storage")
    print("   👤 OAuth 2.0: User account, không giới hạn storage")
    
    print("\n🗂️ File structure sau khi hoàn thành:")
    print("   📁 backend/")
    print("   ├── credentials.json (Service Account - existing)")
    print("   └── oauth_credentials.json (OAuth Client - new)")
    
    print("\n🚀 Sau khi có oauth_credentials.json:")
    print("   python setup_oauth_drive_fixed.py")

def check_existing_files():
    """Kiểm tra các file credentials hiện có"""
    import os
    
    print("\n=" * 70)
    print("📁 KIỂM TRA FILE CREDENTIALS HIỆN TẠI")
    print("=" * 70)
    
    files_to_check = [
        'credentials.json',
        'oauth_credentials.json', 
        'src/google_drive_token.json'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path} - {file_size} bytes")
            
            # Check file type
            if file_path.endswith('credentials.json'):
                try:
                    import json
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    if 'type' in data and data['type'] == 'service_account':
                        print(f"   📊 Type: Service Account")
                        print(f"   📧 Email: {data.get('client_email', 'N/A')}")
                    elif 'installed' in data or 'web' in data:
                        print(f"   👤 Type: OAuth 2.0 Client")
                        client_info = data.get('installed', data.get('web', {}))
                        print(f"   🔑 Client ID: {client_info.get('client_id', 'N/A')[:20]}...")
                    else:
                        print(f"   ❓ Type: Unknown")
                        
                except Exception as e:
                    print(f"   ❌ Error reading file: {e}")
        else:
            print(f"❌ {file_path} - Not found")

def show_next_steps():
    """Hiển thị các bước tiếp theo"""
    import os
    
    print("\n=" * 70)
    print("🎯 CÁC BƯỚC TIẾP THEO")
    print("=" * 70)
    
    if os.path.exists('oauth_credentials.json'):
        print("\n✅ Đã có oauth_credentials.json!")
        print("🚀 Chạy lệnh: python setup_oauth_drive_fixed.py")
    else:
        print("\n❌ Chưa có oauth_credentials.json")
        print("📋 Làm theo hướng dẫn ở trên để tạo OAuth credentials")
        print("💾 Download và save as 'oauth_credentials.json'")
    
    print("\n🔧 Các lệnh hữu ích:")
    print("   python setup_oauth_drive_fixed.py  # Setup OAuth")
    print("   python test_oauth_upload.py        # Test upload")
    print("   python test_simple_drive.py        # Test component")

if __name__ == "__main__":
    create_oauth_credentials_guide()
    check_existing_files() 
    show_next_steps()
