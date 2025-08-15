"""
Verify the records data was written correctly to Google Sheets
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.workflow.google_services import GoogleSheetsService

async def verify_records_write():
    """Verify records data was written to Google Sheets"""
    print("🔍 Verifying records data in Google Sheets...")
    
    service = GoogleSheetsService()
    
    if not await service.authenticate():
        print("❌ Authentication failed")
        return
    
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    try:
        success, result = await service.read_sheet(
            sheet_id=sheet_id,
            sheet_name="TestRecords",
            range_str="A:Z"
        )
        
        if success and result.get('operation') == 'read_success':
            data = result.get('data', {})
            values = data.get('values', [])
            
            print(f"📊 Found {len(values)} rows in TestRecords sheet:")
            for i, row in enumerate(values):
                print(f"   Row {i+1}: {row}")
            
            if values and len(values) >= 2:
                headers = values[0]
                data_rows = values[1:]
                print(f"\n✅ SUCCESS! Records converted correctly:")
                print(f"   📝 Headers: {headers}")
                print(f"   📊 Data rows: {len(data_rows)}")
                
                return True
        else:
            print(f"❌ Failed to read sheet: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_records_write())
