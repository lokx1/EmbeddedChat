#!/usr/bin/env python3
"""
Test if GoogleSheetsService can be imported and used
"""

import sys
import os

# Add the backend source path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_google_sheets_import():
    """Test importing GoogleSheetsService"""
    try:
        print("📊 Testing GoogleSheetsService import...")
        from src.services.workflow.google_services import GoogleSheetsService
        print("✅ GoogleSheetsService imported successfully")
        
        # Test creating service
        print("🔧 Creating GoogleSheetsService instance...")
        service = GoogleSheetsService()
        print("✅ GoogleSheetsService instance created")
        
        # Test authentication
        print("🔐 Testing authentication...")
        import asyncio
        auth_result = asyncio.run(service.authenticate())
        print(f"🔐 Authentication result: {auth_result}")
        
        if auth_result:
            print("🎉 Google Sheets API is ready!")
        else:
            print("⚠️  Google Sheets API authentication failed")
            
        return auth_result
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_credentials():
    """Check if credentials file exists"""
    cred_files = ["credentials.json", "src/credentials.json", "../credentials.json"]
    
    for cred_file in cred_files:
        if os.path.exists(cred_file):
            print(f"✅ Found credentials file: {cred_file}")
            return cred_file
    
    print("❌ No credentials file found")
    print("   Looked for: " + ", ".join(cred_files))
    return None

def test_component_registry_import():
    """Test if component registry can import GoogleSheetsService"""
    try:
        print("\\n📦 Testing component registry import...")
        from src.services.workflow.component_registry import GOOGLE_SHEETS_AVAILABLE
        print(f"🔧 GOOGLE_SHEETS_AVAILABLE: {GOOGLE_SHEETS_AVAILABLE}")
        
        if GOOGLE_SHEETS_AVAILABLE:
            from src.services.workflow.component_registry import GoogleSheetsService
            print("✅ GoogleSheetsService imported in component registry")
        else:
            print("❌ GoogleSheetsService NOT available in component registry")
            
        return GOOGLE_SHEETS_AVAILABLE
        
    except Exception as e:
        print(f"❌ Component registry import error: {e}")
        return False

if __name__ == "__main__":
    print("=== Google Sheets Service Test ===\\n")
    
    # Check credentials
    cred_file = check_credentials()
    
    # Test direct import
    direct_import = test_google_sheets_import()
    
    # Test component registry import
    registry_import = test_component_registry_import()
    
    print(f"\\n📋 Summary:")
    print(f"   - Credentials file: {'✅' if cred_file else '❌'}")
    print(f"   - Direct import: {'✅' if direct_import else '❌'}")
    print(f"   - Registry import: {'✅' if registry_import else '❌'}")
    
    if direct_import and registry_import:
        print("\\n🎉 Google Sheets integration is ready!")
    else:
        print("\\n⚠️  Google Sheets integration needs setup")
