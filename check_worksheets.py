#!/usr/bin/env python3
"""
Check Google Sheets Worksheets
"""

import gspread
from google.oauth2.service_account import Credentials
import sys
import os

def check_worksheets():
    """Check all worksheets in the Google Sheet"""
    print("🔍 CHECKING GOOGLE SHEETS WORKSHEETS")
    print("="*50)
    
    # Set up credentials path
    credentials_path = os.path.join("backend", "credentials.json")
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return
    
    try:
        # Authorize with Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        # Your sheet ID (from the logs)
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        
        # Open the sheet
        sheet = client.open_by_key(sheet_id)
        
        print(f"📊 Sheet Title: {sheet.title}")
        print(f"🆔 Sheet ID: {sheet_id}")
        print(f"🔗 Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
        
        # List all worksheets
        worksheets = sheet.worksheets()
        print(f"\n📄 Found {len(worksheets)} worksheets:")
        
        for i, worksheet in enumerate(worksheets):
            print(f"\n   {i+1}. '{worksheet.title}' (ID: {worksheet.id})")
            
            # Get some basic info
            try:
                row_count = worksheet.row_count
                col_count = worksheet.col_count
                print(f"      Size: {row_count} rows x {col_count} cols")
                
                # Check if it has data
                values = worksheet.get_all_values()
                data_rows = len([row for row in values if any(cell.strip() for cell in row)])
                print(f"      Data rows: {data_rows}")
                
                # Show headers if available
                if len(values) > 0 and any(cell.strip() for cell in values[0]):
                    headers = values[0]
                    print(f"      Headers: {headers}")
                    
                    # Check for Prompt column
                    if "Prompt" in headers:
                        prompt_col_index = headers.index("Prompt")
                        print(f"      🎯 Prompt column found at index {prompt_col_index}")
                        
                        # Check if there's data in Prompt column
                        prompt_data = [row[prompt_col_index] if len(row) > prompt_col_index else "" for row in values[1:]]
                        non_empty_prompts = [p for p in prompt_data if p.strip()]
                        print(f"      💬 Non-empty prompts: {len(non_empty_prompts)}")
                        
                        if non_empty_prompts:
                            print(f"      📝 First prompt: {non_empty_prompts[0][:100]}...")
                    else:
                        print(f"      ❌ No 'Prompt' column found")
                
            except Exception as e:
                print(f"      ❌ Error reading worksheet: {e}")
        
        # Show which one is the default (first)
        if worksheets:
            default_worksheet = worksheets[0]
            print(f"\n🎯 DEFAULT WORKSHEET (when worksheet_name='NOT SET'):")
            print(f"   '{default_worksheet.title}' (ID: {default_worksheet.id})")
        
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    check_worksheets()
