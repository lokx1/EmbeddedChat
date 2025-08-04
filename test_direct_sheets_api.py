#!/usr/bin/env python3
"""
Direct test of Google Sheets API to check authentication and data access
"""
import sys
import os

# Add backend src to path
backend_src_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src_path)

try:
    from services.google_sheets_service import GoogleSheetsService
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"📁 Backend src path: {backend_src_path}")
    print(f"📁 Path exists: {os.path.exists(backend_src_path)}")
    sys.exit(1)

import asyncio

async def test_direct_sheets_access():
    """Test direct access to Google Sheets API"""
    
    print("=== Direct Google Sheets API Test ===")
    
    # Initialize service
    credentials_path = os.path.join(os.path.dirname(__file__), 'backend', 'credentials.json')
    print(f"📁 Credentials path: {credentials_path}")
    print(f"📁 Credentials exist: {os.path.exists(credentials_path)}")
    
    sheets_service = GoogleSheetsService(credentials_path)
    
    # Authenticate
    print("🔐 Attempting authentication...")
    auth_result = await sheets_service.authenticate()
    print(f"🔐 Authentication result: {auth_result}")
    
    if not auth_result:
        print("❌ Authentication failed!")
        return
    
    # Test reading the sheet
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    sheet_name = "Trang tính1"
    range_name = f"{sheet_name}!A1:E10"
    
    print(f"📖 Reading sheet: {range_name}")
    
    try:
        values = sheets_service.read_sheet(sheet_id, range_name)
        
        if values:
            print(f"✅ Successfully read {len(values)} rows")
            print(f"📊 Raw data from API:")
            for i, row in enumerate(values):
                print(f"   Row {i+1}: {row}")
        else:
            print("❌ No data returned from API")
            
        # Try reading a smaller range
        print(f"\n📖 Testing smaller range: A1:E6")
        small_values = sheets_service.read_sheet(sheet_id, f"{sheet_name}!A1:E6")
        
        if small_values:
            print(f"✅ Small range read {len(small_values)} rows")
            for i, row in enumerate(small_values):
                print(f"   Row {i+1}: {row}")
        else:
            print("❌ Small range also returned no data")
            
        # Try reading just A1:A10
        print(f"\n📖 Testing column A only: A1:A10")
        col_a_values = sheets_service.read_sheet(sheet_id, f"{sheet_name}!A1:A10")
        
        if col_a_values:
            print(f"✅ Column A read {len(col_a_values)} rows")
            for i, row in enumerate(col_a_values):
                print(f"   Row {i+1}: {row}")
        
    except Exception as e:
        print(f"💥 Exception during sheet reading: {e}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_direct_sheets_access())
