#!/usr/bin/env python3
"""
Debug Worksheet HEY - Check structure and add Prompt column
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

import gspread
from google.oauth2.service_account import Credentials

def check_and_fix_worksheet_hey():
    """Check worksheet HEY và add Prompt column nếu cần"""
    
    print("🔍 Checking worksheet HEY structure...")
    
    # Setup credentials
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        creds = Credentials.from_service_account_file(
            'backend/credentials.json', 
            scopes=SCOPES
        )
        gc = gspread.authorize(creds)
        
        # Open sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet = gc.open_by_key(sheet_id)
        
        # Check worksheet HEY
        try:
            worksheet = sheet.worksheet("HEY")
            print("✅ Found worksheet HEY")
            
            # Get current headers
            headers = worksheet.row_values(1)
            print(f"📋 Current headers: {headers}")
            
            # Check if Prompt column exists
            if "Prompt" not in headers:
                print("❌ Prompt column NOT found - Adding it...")
                
                # Add Prompt column header
                col_count = len(headers)
                new_col = col_count + 1
                
                worksheet.update_cell(1, new_col, "Prompt")
                print(f"✅ Added Prompt column at position {new_col}")
                
                # Verify
                updated_headers = worksheet.row_values(1)
                print(f"📋 Updated headers: {updated_headers}")
                
            else:
                print("✅ Prompt column already exists")
                
            # Get all data to see current state
            all_values = worksheet.get_all_values()
            print(f"\n📊 Current data in HEY worksheet:")
            for i, row in enumerate(all_values[:6], 1):  # Show first 6 rows
                print(f"Row {i}: {row}")
                
        except gspread.WorksheetNotFound:
            print("❌ Worksheet HEY not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def check_all_worksheets():
    """Check all worksheets in the sheet"""
    
    print("\n🔍 Checking all worksheets...")
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        creds = Credentials.from_service_account_file(
            'backend/credentials.json', 
            scopes=SCOPES
        )
        gc = gspread.authorize(creds)
        
        # Open sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet = gc.open_by_key(sheet_id)
        
        # List all worksheets
        worksheets = sheet.worksheets()
        print(f"📋 Found {len(worksheets)} worksheets:")
        
        for ws in worksheets:
            print(f"\n📄 Worksheet: {ws.title}")
            try:
                headers = ws.row_values(1)
                has_prompt = "Prompt" in headers
                print(f"   Headers: {headers}")
                print(f"   Has Prompt column: {'✅' if has_prompt else '❌'}")
                
                if not has_prompt and ws.title in ["HEY", "TEST121", "YES", "TEST_NEW"]:
                    print(f"   🔧 Adding Prompt column to {ws.title}...")
                    col_count = len(headers)
                    new_col = col_count + 1
                    ws.update_cell(1, new_col, "Prompt")
                    print(f"   ✅ Added Prompt column")
                    
            except Exception as e:
                print(f"   ❌ Error reading {ws.title}: {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Debug Worksheet HEY")
    print("="*50)
    
    # Check and fix HEY worksheet
    check_and_fix_worksheet_hey()
    
    print("\n" + "="*50)
    
    # Check all worksheets
    check_all_worksheets()
    
    print("\n" + "="*50)
    print("✅ Worksheet check completed!")
    print("📋 Next: Re-run workflow to test Prompt column")
