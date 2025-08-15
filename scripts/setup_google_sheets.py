#!/usr/bin/env python3
"""
Google Sheets API Setup Tool
Helps you set up credentials and test the connection
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

def check_credentials_file():
    """Check if credentials file exists"""
    possible_files = [
        "credentials.json",
        "service_account.json",
        "google_credentials.json"
    ]
    
    print("🔍 Checking for credentials file...")
    
    for filename in possible_files:
        if os.path.exists(filename):
            print(f"✅ Found credentials file: {filename}")
            
            # Check if it's a valid JSON
            try:
                with open(filename, 'r') as f:
                    cred_data = json.load(f)
                
                if cred_data.get('type') == 'service_account':
                    print(f"📋 Type: Service Account")
                    print(f"📧 Client Email: {cred_data.get('client_email', 'N/A')}")
                    print(f"🆔 Project ID: {cred_data.get('project_id', 'N/A')}")
                    return filename, 'service_account'
                    
                elif cred_data.get('installed') or cred_data.get('web'):
                    print(f"📋 Type: OAuth2 Client")
                    client_info = cred_data.get('installed') or cred_data.get('web')
                    print(f"🆔 Client ID: {client_info.get('client_id', 'N/A')}")
                    return filename, 'oauth2'
                    
                else:
                    print(f"❓ Unknown credential type in {filename}")
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON in {filename}")
            except Exception as e:
                print(f"❌ Error reading {filename}: {str(e)}")
    
    print("❌ No credentials file found")
    return None, None

def setup_instructions():
    """Show setup instructions"""
    print("\n" + "="*60)
    print("📚 GOOGLE SHEETS API SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n🔧 Method 1: Service Account (Recommended for servers)")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select existing project")
    print("3. Enable Google Sheets API:")
    print("   - APIs & Services > Library > Search 'Google Sheets API' > Enable")
    print("4. Create Service Account:")
    print("   - APIs & Services > Credentials > Create Credentials > Service Account")
    print("   - Download the JSON key file")
    print("5. Share your Google Sheets with the service account email")
    print("6. Rename the JSON file to 'service_account.json' and place it in this directory")
    
    print("\n🔧 Method 2: OAuth2 (For personal use)")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select existing project")
    print("3. Enable Google Sheets API")
    print("4. Create OAuth2 Credentials:")
    print("   - APIs & Services > Credentials > Create Credentials > OAuth 2.0 Client IDs")
    print("   - Application type: Desktop application")
    print("   - Download the JSON file")
    print("5. Rename the JSON file to 'credentials.json' and place it in this directory")
    
    print("\n📋 Required Scopes:")
    print("   - https://www.googleapis.com/auth/spreadsheets")
    print("   - https://www.googleapis.com/auth/drive.file")

def test_connection(credentials_file, cred_type):
    """Test Google Sheets API connection"""
    print(f"\n🧪 Testing connection with {credentials_file}...")
    
    try:
        from src.services.google_sheets_service import GoogleSheetsService
        
        # Create service with credentials
        service = GoogleSheetsService(credentials_file)
        
        # Test authentication
        if service.authenticate():
            print("✅ Authentication successful!")
            
            # Test with a public sheet (Google's example sheet)
            test_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            test_range = "Class Data!A1:E5"
            
            print(f"🧪 Testing read access with public sheet...")
            data = service.read_sheet(test_sheet_id, test_range)
            
            if data:
                print(f"✅ Read test successful! Retrieved {len(data)} rows")
                print("📋 Sample data:")
                for i, row in enumerate(data[:3]):
                    print(f"   Row {i+1}: {row}")
                
                # Get sheet info
                info = service.get_sheet_info(test_sheet_id)
                if info:
                    print(f"📊 Sheet info: {info['title']}")
                    print(f"📄 Available sheets: {[s['title'] for s in info['sheets']]}")
                
                return True
            else:
                print("❌ Read test failed")
                return False
        else:
            print("❌ Authentication failed")
            return False
            
    except ImportError:
        print("❌ Google Sheets service not available. Make sure dependencies are installed.")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False

def test_write_access():
    """Test write access with user's sheet"""
    sheet_id = input("\n📝 Enter your Google Sheets ID to test write access (or press Enter to skip): ").strip()
    
    if not sheet_id:
        print("⏭️ Skipping write test")
        return True
    
    try:
        from src.services.google_sheets_service import GoogleSheetsService
        
        service = GoogleSheetsService()
        if not service.authenticate():
            print("❌ Authentication failed")
            return False
        
        # Test data
        test_data = [
            ["Test", "Timestamp", "Status"],
            ["API Test", str(datetime.now()), "Success"]
        ]
        
        # Try to write to a test sheet
        sheet_name = input("📄 Enter sheet name to test (default: Sheet1): ").strip() or "Sheet1"
        range_name = f"{sheet_name}!A1"
        
        print(f"✍️ Testing write to {sheet_id}, {range_name}...")
        
        success = service.write_sheet(sheet_id, range_name, test_data)
        
        if success:
            print("✅ Write test successful!")
            print(f"🔗 Check your sheet: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
            return True
        else:
            print("❌ Write test failed. Check permissions.")
            return False
            
    except Exception as e:
        print(f"❌ Write test failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Google Sheets API Setup & Test Tool")
    print("="*50)
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check for credentials
    cred_file, cred_type = check_credentials_file()
    
    if not cred_file:
        setup_instructions()
        print(f"\n❗ Please follow the instructions above and place your credentials file in:")
        print(f"   {current_dir}")
        return
    
    # Test connection
    if test_connection(cred_file, cred_type):
        print(f"\n🎉 Google Sheets API is working correctly!")
        
        # Ask for write test
        if input("\n❓ Do you want to test write access? (y/N): ").lower().startswith('y'):
            test_write_access()
    
    print(f"\n✅ Setup complete! You can now use Google Sheets API in your workflows.")
    print(f"🔗 Your sheet: https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)
