#!/usr/bin/env python3
"""
Check worksheet status for Prompt column
"""

import gspread
from google.oauth2.service_account import Credentials

def check_worksheets_for_prompt():
    """Check if Prompt column exists in worksheets"""
    print("🔍 CHECKING WORKSHEETS FOR PROMPT COLUMN")
    print("="*45)
    
    try:
        # Set up credentials
        credentials_path = "credentials.json"
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet = client.open_by_key(sheet_id)
        
        print(f"📊 Sheet: {sheet.title}")
        
        # Check all worksheets
        worksheets = sheet.worksheets()
        
        for i, worksheet in enumerate(worksheets[:6]):  # Check first 6
            print(f"\n📄 {i+1}. {worksheet.title}")
            
            try:
                # Get headers
                headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
                
                print(f"   📊 Headers: {headers}")
                
                if "Prompt" in headers:
                    prompt_index = headers.index("Prompt")
                    print(f"   🎯 Prompt column at index {prompt_index} ✅")
                    
                    # Check for recent data
                    all_values = worksheet.get_all_values()
                    recent_prompts = []
                    
                    # Check last 3 rows for Prompt data
                    for row_idx in range(max(1, len(all_values) - 3), len(all_values)):
                        if row_idx < len(all_values):
                            row = all_values[row_idx]
                            if len(row) > prompt_index and row[prompt_index].strip():
                                recent_prompts.append((row_idx + 1, row[prompt_index]))
                    
                    if recent_prompts:
                        print(f"   💬 Recent Prompt entries: {len(recent_prompts)}")
                        for row_num, prompt in recent_prompts[-1:]:  # Show latest
                            print(f"      Row {row_num}: {prompt[:80]}...")
                    else:
                        print(f"   📝 Prompt column exists but no data")
                else:
                    print(f"   ❌ No Prompt column")
                    
                    # Check if this worksheet was recently updated
                    data_rows = len([row for row in worksheet.get_all_values() if any(cell.strip() for cell in row)])
                    print(f"   📊 Total data rows: {data_rows}")
                    
            except Exception as e:
                print(f"   ❌ Error reading worksheet: {e}")
    
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    check_worksheets_for_prompt()
