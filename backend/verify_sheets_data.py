"""
Verify Google Sheets Data         # Try to read the sheet data
        success, result = await service.read_sheet(
            sheet_id=sheet_id,
            range_str="A:Z"
        )
        
        print(f"📊 Read success: {success}")
        
        if success and result.get('operation') == 'read_success':
            data = result.get('data', {})
            values = data.get('values', [])
            print(f"📊 Found {len(values)} rows of data")
            
            if values:
                print("📝 Data from Google Sheets:")
                for i, row in enumerate(values):  # Show all rows
                    print(f"   Row {i+1}: {row}")
                    
                print(f"\n✅ SUCCESS! Data was written to Google Sheets!")
                print(f"   📄 Sheet: {result['sheet_info']['title']}")
                print(f"   📊 Worksheet: {result['sheet_info']['sheet_name']}")
                print(f"   📝 Rows: {data['rows_count']}, Columns: {data['columns_count']}")
            else:
                print("❌ No data found in sheet")
        else:
            print(f"❌ Failed to read sheet: {result}")ck if data was actually written to the Google Sheet
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.workflow.google_services import GoogleSheetsService
import asyncio

async def verify_sheets_data():
    """Verify that data was written to Google Sheets"""
    print("🔍 Verifying Google Sheets Data...")
    
    # Initialize service
    service = GoogleSheetsService()
    
    # Authenticate first
    if not await service.authenticate():
        print("❌ Authentication failed")
        return
    
    # Sheet ID from debug script
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    try:
        # Read sheet data using the existing methods
        print(f"📋 Reading from Sheet ID: {sheet_id}")
        
        # Try to read the sheet data
        result = await service.read_sheet(
            sheet_id=sheet_id,
            range_str="A:Z"
        )
        
        print(f"� Read result: {result}")
        
        if result.get('operation') == 'read_success':
            data = result.get('data', [])
            print(f"📊 Found {len(data)} rows of data")
            
            if data:
                print("📝 Sample data:")
                for i, row in enumerate(data[:5]):  # Show first 5 rows
                    print(f"   Row {i+1}: {row}")
            else:
                print("❌ No data found in sheet")
        else:
            print(f"❌ Failed to read sheet: {result}")
        
        print("\n✅ Verification complete!")
        
    except Exception as e:
        print(f"❌ Error verifying sheets data: {e}")
        import traceback
        traceback.print_exc()

def main():
    asyncio.run(verify_sheets_data())

if __name__ == "__main__":
    main()
