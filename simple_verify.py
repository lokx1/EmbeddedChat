#!/usr/bin/env python3
"""
Simple verification that data was written to Google Sheets
"""

import sys
import os
import asyncio

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

async def verify_data():
    try:
        from src.services.workflow.google_services import GoogleSheetsService
        
        print("🔍 Reading data from Google Sheets HEYDO worksheet...")
        
        service = GoogleSheetsService(credentials_path=os.path.join(backend_path, "credentials.json"))
        
        # Authenticate first
        auth_success = await service.authenticate()
        if not auth_success:
            print("❌ Authentication failed")
            return
            
        result = await service.read_sheet(
            sheet_id='1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc', 
            sheet_name='HEYDO',
            range_str='A1:E10'
        )
        
        if result[0]:  # result is a tuple (success, data)
            data = result[1]["data"]
            print(f"✅ Read {len(data)} rows from Google Sheets")
            
            for i, row in enumerate(data):
                print(f"Row {i+1}: {row}")
                
                # Handle different data structures
                if isinstance(row, list):
                    # Check Prompt column (column E, index 4)
                    if i > 0 and len(row) >= 5 and row[4]:
                        print(f"   ✅ Prompt: {row[4][:80]}...")
                else:
                    print(f"   📋 Row type: {type(row)}")
                    
            # Summary - handle different data types
            try:
                if data and isinstance(data[0], list):
                    prompt_rows = sum(1 for row in data[1:] if isinstance(row, list) and len(row) >= 5 and row[4])
                else:
                    prompt_rows = 0  # Different data structure
                    
                print(f"\n🎯 SUMMARY:")
                print(f"   Total rows: {len(data)}")
                print(f"   Data type: {type(data)}")
                
                if prompt_rows > 0:
                    print(f"   Rows with AI prompts: {prompt_rows}")
                    print(f"   🎉 SUCCESS! AI responses are in your Google Sheets!")
                else:
                    print(f"   ❓ Data structure may be different - check the sheet manually")
                    print(f"   🔍 Go to your Google Sheets HEYDO worksheet and check column E (Prompt)")
            except Exception as e:
                print(f"   ⚠️ Error analyzing data: {e}")
                print(f"   🔍 Check your Google Sheets manually for the data")
        else:
            print(f"❌ Failed to read: {result[1]}")
            
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_data())
