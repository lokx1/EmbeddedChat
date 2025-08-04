#!/usr/bin/env python3
"""
Direct test of Google Sheets API to check authentication and data access
"""
import sys
import os
from src.services.google_sheets_service import GoogleSheetsService
import asyncio

async def test_direct_sheets_access():
    """Test direct access to Google Sheets API"""
    
    print("=== Direct Google Sheets API Test ===")
    
    # Initialize service
    credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    print(f"📁 Credentials path: {credentials_path}")
    print(f"📁 Credentials exist: {os.path.exists(credentials_path)}")
    
    sheets_service = GoogleSheetsService(credentials_path)
    
    # Authenticate
    print("🔐 Attempting authentication...")
    auth_result = sheets_service.authenticate()
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
                
        # Test with exact range that has data
        print(f"\n📖 Testing exact data range: A1:E6")
        exact_values = sheets_service.read_sheet(sheet_id, f"{sheet_name}!A1:E6")
        
        if exact_values:
            print(f"✅ Exact range read {len(exact_values)} rows")
            print(f"📊 Exact data:")
            for i, row in enumerate(exact_values):
                print(f"   Row {i+1}: {row}")
                
            # Analyze the data structure
            if len(exact_values) > 1:
                headers = exact_values[0] if exact_values else []
                data_rows = exact_values[1:] if len(exact_values) > 1 else []
                print(f"\n📋 Data Analysis:")
                print(f"   Headers: {headers}")
                print(f"   Data rows: {len(data_rows)}")
                
                # Convert to records manually
                records = []
                for row in data_rows:
                    if any(str(cell).strip() for cell in row if cell is not None):  # Row has content
                        record = {}
                        for i, header in enumerate(headers):
                            value = row[i] if i < len(row) else ""
                            record[header] = str(value).strip() if value is not None else ""
                        records.append(record)
                
                print(f"   Converted records: {len(records)}")
                for i, record in enumerate(records):
                    print(f"   Record {i+1}: {record}")
        
    except Exception as e:
        print(f"💥 Exception during sheet reading: {e}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_direct_sheets_access())
