#!/usr/bin/env python3
"""
Test Google Sheets API with correct sheet name - HEYDO
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.google_sheets_service import GoogleSheetsService
import asyncio

def test_correct_sheet_name():
    """Test with correct sheet name HEYDO"""
    
    print("=== Testing Google Sheets API with Correct Sheet Name ===")
    
    # Correct sheet details
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    sheet_name = "HEYDO"  # ✅ Correct sheet name!
    range_name = "A1:E10"
    
    try:
        # Initialize service
        credentials_path = "credentials.json"
        sheets_service = GoogleSheetsService(credentials_path)
        
        print(f"🔧 Using sheet ID: {sheet_id}")
        print(f"🔧 Using sheet name: {sheet_name}")
        print(f"🔧 Using range: {range_name}")
        
        # Authenticate
        print("🔐 Authenticating...")
        auth_result = sheets_service.authenticate()
        print(f"✅ Authentication: {auth_result}")
        
        if not auth_result:
            print("❌ Authentication failed")
            return False
        
        # Read data
        print(f"📖 Reading data from sheet '{sheet_name}'...")
        range_full = f"{sheet_name}!{range_name}"
        values = sheets_service.read_sheet(sheet_id, range_full)
        
        print(f"📊 Read result: {values is not None}")
        
        if values:
            print(f"📊 Raw values count: {len(values)}")
            
            # Show raw values
            for i, row in enumerate(values):
                print(f"   Row {i+1}: {row}")
            
            # Convert to records manually (similar to GoogleSheetsComponent logic)
            if len(values) > 0:
                headers = values[0]  # First row as headers
                records = []
                
                for row_data in values[1:]:  # Skip header row
                    if any(cell.strip() for cell in row_data if cell):  # Skip empty rows
                        record = {}
                        for i, header in enumerate(headers):
                            value = row_data[i] if i < len(row_data) else ""
                            record[header] = value
                        records.append(record)
                
                print(f"📊 Records count: {len(records)}")
                
                if records:
                    print("📋 Records:")
                    for i, record in enumerate(records):
                        print(f"   Record {i+1}: {record}")
                        
                    # Check first record for AI processing
                    if len(records) > 0:
                        first_record = records[0]
                        print(f"\n🎯 First record for AI processing:")
                        print(f"   Description: {first_record.get('Description', 'N/A')}")
                        print(f"   Output Format: {first_record.get('Desired Output Format', 'N/A')}")
                        print(f"   Model: {first_record.get('Model Specification', 'N/A')}")
                        print(f"   Current Prompt: {first_record.get('Prompt', 'EMPTY')}")
                        
                else:
                    print("❌ No records found after conversion")
                    
        else:
            print(f"❌ Failed to read sheet data")
            
        return values is not None
        
    except Exception as e:
        print(f"💥 Exception: {e}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    result = test_correct_sheet_name()
    if result:
        print("\n🎉 SUCCESS: Sheet reading works with correct name!")
    else:
        print("\n❌ FAILED: Still issues with sheet reading")
