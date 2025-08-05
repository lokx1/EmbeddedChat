#!/usr/bin/env python3
"""
Test Google Sheets reading to understand input data structure
"""

import sys
sys.path.append('d:/EmbeddedChat/backend/src')

import asyncio
from services.google_sheets.google_sheets_service import GoogleSheetsService

async def test_sheets_reading():
    print("📋 Testing Google Sheets reading to understand input structure...")
    
    try:
        sheets_service = GoogleSheetsService()
        
        # Authenticate
        print("🔐 Authenticating...")
        auth_result = await sheets_service.authenticate()
        print(f"Auth result: {auth_result}")
        
        if not auth_result:
            print("❌ Authentication failed")
            return
        
        # Read the sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet_name = "HEYDO"
        range_name = "A1:Z100"
        
        print(f"📖 Reading sheet: {sheet_id}")
        print(f"   Sheet name: {sheet_name}")
        print(f"   Range: {range_name}")
        
        success, result = await sheets_service.read_sheet(sheet_id, sheet_name, range_name)
        print(f"Read result: success={success}")
        
        if success and result:
            records = result.get("records", [])
            print(f"\n📊 Found {len(records)} records")
            
            if records:
                print(f"\n🔍 First record structure:")
                first_record = records[0]
                print(f"   Type: {type(first_record)}")
                print(f"   Keys: {list(first_record.keys()) if isinstance(first_record, dict) else 'Not a dict'}")
                print(f"   Content: {first_record}")
                
                # Check if Prompt column exists and what it contains
                if isinstance(first_record, dict) and "Prompt" in first_record:
                    prompt_value = first_record["Prompt"]
                    print(f"\n🎯 Prompt column analysis:")
                    print(f"   Type: {type(prompt_value)}")
                    print(f"   Value: '{prompt_value}'")
                    print(f"   Length: {len(str(prompt_value))}")
                    print(f"   Is empty: {not prompt_value or str(prompt_value).strip() == ''}")
                
                # Check other columns that might be relevant
                for key, value in first_record.items():
                    print(f"   {key}: '{value}' (type: {type(value)})")
                
                print(f"\n📋 Sample records (first 3):")
                for i, record in enumerate(records[:3]):
                    print(f"   Record {i+1}: {record}")
        
        else:
            print(f"❌ Failed to read sheet: {result}")
    
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sheets_reading())
