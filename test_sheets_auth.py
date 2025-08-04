#!/usr/bin/env python3
"""
Test Google Sheets Authentication
"""
import sys
import os
import asyncio

# Add backend src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.workflow.google_services import GoogleSheetsService

async def test_auth():
    print("🔐 Testing Google Sheets Authentication")
    print("="*40)
    
    try:
        # Use correct credentials path
        credentials_path = os.path.join(os.path.dirname(__file__), 'backend', 'credentials.json')
        print(f"📁 Credentials path: {credentials_path}")
        print(f"📁 Exists: {os.path.exists(credentials_path)}")
        
        service = GoogleSheetsService(credentials_path)
        print(f"✅ Service created")
        
        auth_result = await service.authenticate()
        print(f"🔐 Authentication result: {auth_result}")
        
        if auth_result:
            print("✅ Google Sheets API authentication successful!")
            
            # Test basic read operation
            sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
            try:
                success, result = await service.read_sheet(sheet_id, "Sheet1", "A1:F10")
                print(f"📊 Test read result: {success}")
                if success:
                    print("✅ Google Sheets API read working!")
                else:
                    print(f"❌ Read failed: {result}")
            except Exception as e:
                print(f"❌ Read error: {e}")
                
        else:
            print("❌ Google Sheets API authentication failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth())
