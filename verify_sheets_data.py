#!/usr/bin/env python3
"""
Verify that the AI responses were actually written to Google Sheets
"""

import sys
import os
import asyncio

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from src.services.google_services import GoogleSheetsService

async def verify_sheets_data():
    """Verify the data was written to Google Sheets"""
    print("🔍 VERIFYING: Google Sheets Data")
    print("="*50)
    
    # Initialize Google Sheets service
    sheets_service = GoogleSheetsService()
    
    # Your sheet details
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    sheet_name = "HEYDO"
    
    try:
        print(f"📊 Reading data from {sheet_name} worksheet...")
        
        # Read the data that was just written
        result = await sheets_service.read_from_sheet(
            sheet_id=sheet_id,
            range_name=f"{sheet_name}!A1:E10"  # Read first 10 rows, 5 columns
        )
        
        if result["success"]:
            data = result["data"]
            print(f"✅ Successfully read {len(data)} rows from Google Sheets")
            print(f"")
            
            # Display the data
            for i, row in enumerate(data):
                print(f"Row {i+1}: {row}")
                
                # Check if this is a data row (not header) and has a Prompt column
                if i > 0 and len(row) >= 5:  # Skip header, check if has 5 columns
                    prompt_text = row[4] if len(row) > 4 else ""
                    if prompt_text:
                        print(f"   ✅ Prompt found: {prompt_text[:100]}...")
                    else:
                        print(f"   ❌ No prompt data in this row")
                        
            print(f"")
            print(f"🎯 VERIFICATION RESULT:")
            
            # Check if we have the expected data structure
            if len(data) >= 5:  # Header + 4 data rows
                headers = data[0]
                if "Prompt" in headers:
                    prompt_index = headers.index("Prompt")
                    prompt_data_count = 0
                    
                    for row in data[1:]:  # Skip header
                        if len(row) > prompt_index and row[prompt_index]:
                            prompt_data_count += 1
                    
                    print(f"✅ Headers found: {headers}")
                    print(f"✅ Prompt column at index: {prompt_index}")
                    print(f"✅ Rows with Prompt data: {prompt_data_count}")
                    
                    if prompt_data_count > 0:
                        print(f"")
                        print(f"🎉 SUCCESS! AI responses ARE written to Google Sheets!")
                        print(f"   - Total rows with AI prompts: {prompt_data_count}")
                        print(f"   - Check column E (Prompt) in your HEYDO worksheet")
                        print(f"   - Refresh your browser if you don't see the data")
                    else:
                        print(f"")
                        print(f"❌ No AI prompt data found in Prompt column")
                else:
                    print(f"❌ Prompt column not found in headers: {headers}")
            else:
                print(f"❌ Not enough data rows found. Expected 5, got {len(data)}")
                
        else:
            print(f"❌ Failed to read from Google Sheets: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"💥 Exception during verification: {str(e)}")

if __name__ == "__main__":
    asyncio.run(verify_sheets_data())
