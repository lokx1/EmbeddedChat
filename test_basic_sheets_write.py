#!/usr/bin/env python3
"""
Test Basic Google Sheets Write
Kiểm tra xem có thể write vào Google Sheets không với credentials hiện tại
"""

import os
import sys
import asyncio

# Add backend path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "src")
sys.path.insert(0, backend_dir)

async def test_basic_write():
    """Test basic Google Sheets write functionality"""
    print("📊 TESTING BASIC GOOGLE SHEETS WRITE")
    print("="*50)
    
    try:
        # Import the service from backend
        from services.workflow.google_services import GoogleSheetsService
        
        # Use the credentials.json from backend folder
        credentials_path = os.path.join("backend", "credentials.json")
        
        if not os.path.exists(credentials_path):
            print(f"❌ Credentials file not found: {credentials_path}")
            return False
            
        print(f"✅ Credentials file found: {credentials_path}")
        
        # Create service
        print(f"🔧 Creating GoogleSheetsService...")
        sheets_service = GoogleSheetsService(credentials_path)
        
        # Test authentication
        print(f"🔐 Testing authentication...")
        auth_result = await sheets_service.authenticate()
        print(f"   Auth result: {auth_result}")
        
        if not auth_result:
            print(f"❌ Authentication failed!")
            return False
            
        print(f"✅ Authentication successful!")
        
        # Test data to write
        test_data = [
            ["Test Header 1", "Test Header 2", "Test Header 3", "Status", "URL", "Prompt Column"],
            ["Data Row 1A", "Data Row 1B", "Data Row 1C", "Success", "https://test1.com", "This is AI response 1"],
            ["Data Row 2A", "Data Row 2B", "Data Row 2C", "Success", "https://test2.com", "This is AI response 2"],
            ["Data Row 3A", "Data Row 3B", "Data Row 3C", "Success", "https://test3.com", "This is AI response 3"]
        ]
        
        print(f"📊 Test data prepared:")
        for i, row in enumerate(test_data):
            print(f"   Row {i}: {row}")
        
        # Sheet configuration
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet_name = "Basic_Test"
        range_start = "A1"
        mode = "overwrite"
        
        print(f"\n🔧 Writing to Google Sheets...")
        print(f"   Sheet ID: {sheet_id}")
        print(f"   Sheet Name: {sheet_name}")
        print(f"   Range: {range_start}")
        print(f"   Mode: {mode}")
        
        # Attempt to write
        success, result = await sheets_service.write_to_sheet(
            sheet_id, sheet_name, range_start, mode, test_data
        )
        
        print(f"\n📊 Write Result:")
        print(f"   Success: {success}")
        print(f"   Result: {result}")
        
        if success:
            print(f"\n🎉 SUCCESS! Data written to Google Sheets!")
            print(f"📝 Check your sheet at: https://docs.google.com/spreadsheets/d/{sheet_id}")
            
            # Test reading back to verify
            print(f"\n🔍 Verifying data by reading back...")
            read_success, read_data = await sheets_service.read_from_sheet(
                sheet_id, sheet_name, "A1:F10"
            )
            
            if read_success:
                print(f"✅ Read back successful:")
                for i, row in enumerate(read_data):
                    print(f"   Row {i}: {row}")
            else:
                print(f"❌ Read back failed: {read_data}")
                
            return True
        else:
            print(f"\n❌ FAILED! Error: {result}")
            return False
            
    except Exception as e:
        print(f"\n💥 EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_basic_write())
    
    if result:
        print(f"\n✅ BASIC WRITE TEST PASSED!")
        print(f"🎯 Google Sheets write functionality is working")
        print(f"📊 Your AI_Response can be written to sheets")
    else:
        print(f"\n❌ BASIC WRITE TEST FAILED!")
        print(f"💡 Need to fix authentication or permissions")
