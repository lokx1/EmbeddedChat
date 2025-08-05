#!/usr/bin/env python3
"""
Test Google Sheets Write Method Directly
"""

import asyncio
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "src")
sys.path.insert(0, backend_dir)

async def test_write_method():
    """Test the GoogleSheetsWriteComponent._write_to_google_sheets method directly"""
    print("🔧 TESTING GOOGLE SHEETS WRITE METHOD DIRECTLY")
    print("="*55)
    
    try:
        from services.workflow.component_registry import GoogleSheetsWriteComponent
        
        # Create instance
        component = GoogleSheetsWriteComponent()
        
        # Test data to write
        test_data = [
            ["Header 1", "Header 2", "Header 3", "Status", "URL", "Prompt"],
            ["Test Data 1", "Test Data 2", "Test Data 3", "Success", "https://test.com", "This is test AI response"],
            ["Test Data A", "Test Data B", "Test Data C", "Success", "https://example.com", "Another AI response here"]
        ]
        
        print(f"📊 Test data prepared:")
        for i, row in enumerate(test_data):
            print(f"   Row {i}: {row}")
        
        # Test the write method
        print(f"\n🔧 Calling _write_to_google_sheets method...")
        success, result_data = await component._write_to_google_sheets(
            sheet_id="1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            sheet_name="Auth_Test",
            range_start="A1",
            mode="overwrite",
            data=test_data
        )
        
        print(f"\n📊 Result:")
        print(f"   Success: {success}")
        print(f"   Result data: {result_data}")
        
        if success:
            print(f"\n🎉 SUCCESS! Data was written to Google Sheets!")
            return True
        else:
            print(f"\n❌ FAILED! Error: {result_data}")
            return False
            
    except Exception as e:
        print(f"\n💥 EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_write_method())
    
    if result:
        print(f"\n✅ Google Sheets Write Method Working!")
        print(f"📊 Your AI_Response should now be in Google Sheets")
    else:
        print(f"\n❌ Google Sheets Write Method Failed!")
        print(f"💡 Check authentication and credentials")
