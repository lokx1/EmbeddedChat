#!/usr/bin/env python3
"""Check if data was written to Test sheet"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.google_sheets_service import GoogleSheetsService
import time

def main():
    print("🔍 Checking Test Sheet Data After Workflow Execution")
    print("=" * 60)
    
    # Wait a bit for async processing
    print("⏳ Waiting 5 seconds for background processing...")
    time.sleep(5)
    
    service = GoogleSheetsService()
    
    if not service.authenticate():
        print("❌ Failed to authenticate")
        return
    
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    try:
        # Check Test sheet
        print("\n📊 Checking Test sheet:")
        test_data = service.read_sheet(sheet_id, "Test!A1:D20")
        if test_data:
            print(f"✅ Found {len(test_data)} rows in Test sheet:")
            for i, row in enumerate(test_data):
                print(f"  Row {i+1}: {row}")
        else:
            print("📋 No data found in Test sheet")
            
        # Compare with Result_Test sheet
        print("\n📊 Checking Result_Test sheet for comparison:")
        result_data = service.read_sheet(sheet_id, "Result_Test!A1:D20")
        if result_data:
            print(f"✅ Found {len(result_data)} rows in Result_Test sheet:")
            for i, row in enumerate(result_data):
                print(f"  Row {i+1}: {row}")
        else:
            print("📋 No data found in Result_Test sheet")
            
        # Check all sheets to see what's available
        print("\n📋 Checking all available sheets:")
        sheet_info = service.get_sheet_info(sheet_id)
        if sheet_info:
            sheets = [sheet['title'] for sheet in sheet_info.get('sheets', [])]
            print(f"Available sheets: {sheets}")
            
    except Exception as e:
        print(f"❌ Error reading sheet: {e}")

if __name__ == "__main__":
    main()
