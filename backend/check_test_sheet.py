#!/usr/bin/env python3
"""Check Test sheet data"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from services.google_sheets_service import GoogleSheetsService

def main():
    print("🔍 Checking Test sheet data...")
    time.sleep(3)  # Wait for processing
    
    service = GoogleSheetsService()
    if not service.authenticate():
        print("❌ Failed to authenticate")
        return
    
    sheet_id = '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc'
    
    try:
        data = service.read_sheet(sheet_id, 'Test!A1:D10')
        print(f'📊 Data in Test sheet ({len(data) if data else 0} rows):')
        if data:
            for i, row in enumerate(data):
                print(f'  Row {i+1}: {row}')
        else:
            print("  No data found")
    except Exception as e:
        print(f"❌ Error reading sheet: {e}")
    
    # Also check Result_Test for comparison
    try:
        result_data = service.read_sheet(sheet_id, 'Result_Test!A1:D10')
        print(f'\n📊 Data in Result_Test sheet ({len(result_data) if result_data else 0} rows):')
        if result_data:
            for i, row in enumerate(result_data):
                print(f'  Row {i+1}: {row}')
    except Exception as e:
        print(f"❌ Error reading Result_Test sheet: {e}")

if __name__ == "__main__":
    main()
