#!/usr/bin/env python3
"""
Check Google Sheets structure and available worksheets
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
from src.services.workflow.google_services import GoogleSheetsService

async def check_sheet_structure():
    """Check the structure of your Google Sheets"""
    
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    print(f"🔍 Checking Google Sheets structure")
    print(f"🔗 Sheet ID: {sheet_id}")
    
    try:
        # Create Google Sheets service
        service = GoogleSheetsService()
        
        # Authenticate
        auth_result = await service.authenticate()
        if not auth_result:
            print("❌ Authentication failed")
            return
            
        print("✅ Authentication successful")
        
        # Get sheet information
        sheet = service.client.open_by_key(sheet_id)
        print(f"📊 Sheet title: {sheet.title}")
        
        # List all worksheets
        worksheets = sheet.worksheets()
        print(f"📋 Found {len(worksheets)} worksheets:")
        
        for i, worksheet in enumerate(worksheets):
            print(f"   {i+1}. {worksheet.title} (ID: {worksheet.id})")
            print(f"      Size: {worksheet.row_count} rows x {worksheet.col_count} cols")
            
            # Get first few rows to see data
            try:
                if worksheet.row_count > 0:
                    first_rows = worksheet.get('A1:Z5')  # Get first 5 rows
                    print(f"      Sample data ({len(first_rows)} rows):")
                    for row_idx, row in enumerate(first_rows[:3]):
                        print(f"        Row {row_idx+1}: {row}")
                else:
                    print("      (Empty worksheet)")
            except Exception as e:
                print(f"      Error reading data: {e}")
                
        # Test reading with different sheet names
        print(f"\\n🔧 Testing read methods:")
        
        # Try reading from first worksheet
        if worksheets:
            first_sheet = worksheets[0]
            print(f"\\n📖 Reading from '{first_sheet.title}':")
            
            try:
                # Test synchronous read_sheet method
                values = service.read_sheet(sheet_id, f"{first_sheet.title}!A1:E10")
                print(f"✅ read_sheet success: {len(values)} rows")
                if values:
                    print(f"   Headers: {values[0] if values else 'None'}")
                    
            except Exception as e:
                print(f"❌ read_sheet error: {e}")
                
            try:
                # Test asynchronous read_sheet_data method  
                records = await service.read_sheet_data(sheet_id, "A1:E10")
                print(f"✅ read_sheet_data success: {len(records)} records")
                if records:
                    print(f"   First record keys: {list(records[0].keys()) if records else 'None'}")
                    
            except Exception as e:
                print(f"❌ read_sheet_data error: {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=== Google Sheets Structure Check ===\\n")
    asyncio.run(check_sheet_structure())
