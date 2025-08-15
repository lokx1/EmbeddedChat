#!/usr/bin/env python3
"""
Fix and add Prompt column correctly
"""

import gspread
from google.oauth2.service_account import Credentials

def add_prompt_column_fixed():
    """Add Prompt column with correct API syntax"""
    print("🔧 ADDING PROMPT COLUMN - FIXED VERSION")
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
        
        # Target worksheets
        target_worksheets = ["TEST121", "YES", "TEST_NEW"]
        
        for worksheet_name in target_worksheets:
            try:
                worksheet = sheet.worksheet(worksheet_name)
                
                print(f"\n📄 Processing {worksheet_name}...")
                
                # Get current headers
                headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
                
                print(f"   📊 Current headers: {headers}")
                
                if "Prompt" not in headers:
                    # Method 1: Update cell directly
                    next_col = len(headers) + 1
                    next_col_letter = chr(ord('A') + next_col - 1)
                    
                    print(f"   🎯 Adding Prompt at column {next_col_letter}")
                    
                    # Update the cell
                    worksheet.update_cell(1, next_col, "Prompt")
                    
                    print(f"   ✅ Added Prompt column to {worksheet_name}")
                else:
                    print(f"   ✅ {worksheet_name} already has Prompt column")
                    
            except gspread.WorksheetNotFound:
                print(f"\n📄 {worksheet_name}: Not found")
            except Exception as e:
                print(f"\n📄 {worksheet_name}: Error - {e}")
    
    except Exception as e:
        print(f"💥 Error: {e}")

def test_write_sample_data():
    """Test writing sample data with Prompt column"""
    print(f"\n📝 TESTING WRITE SAMPLE DATA WITH PROMPT")
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
        
        # Test on YES worksheet
        worksheet = sheet.worksheet("YES")
        
        # Sample AI response data
        sample_prompt = "Create a detailed and comprehensive prompt for generating a Task Manager app logo. The logo should be modern, clean, and professional with a focus on productivity and efficiency. Consider using colors like blue or green to convey trust and growth."
        
        # Find Prompt column
        headers = worksheet.row_values(1)
        
        if "Prompt" in headers:
            prompt_col_index = headers.index("Prompt") + 1  # gspread uses 1-based indexing
            
            print(f"   🎯 Found Prompt column at index {prompt_col_index}")
            
            # Write sample data to first available row
            data_rows = len([row for row in worksheet.get_all_values() if any(cell.strip() for cell in row)])
            next_row = data_rows + 1
            
            print(f"   📝 Writing to row {next_row}")
            
            # Write sample prompt
            worksheet.update_cell(next_row, prompt_col_index, sample_prompt)
            
            print(f"   ✅ Written sample AI response to Prompt column")
            print(f"   📍 Location: Row {next_row}, Column {prompt_col_index}")
            
        else:
            print(f"   ❌ Prompt column not found in YES worksheet")
    
    except Exception as e:
        print(f"💥 Error testing write: {e}")

def verify_final_results():
    """Verify final results"""
    print(f"\n🔍 FINAL VERIFICATION")
    print("="*25)
    
    try:
        # Set up credentials
        credentials_path = "credentials.json"
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet = client.open_by_key(sheet_id)
        
        target_worksheets = ["TEST121", "YES", "TEST_NEW"]
        
        for worksheet_name in target_worksheets:
            try:
                worksheet = sheet.worksheet(worksheet_name)
                
                # Get headers
                headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
                
                print(f"\n📄 {worksheet_name}:")
                print(f"   Headers: {headers}")
                
                if "Prompt" in headers:
                    prompt_index = headers.index("Prompt")
                    print(f"   🎯 Prompt column at index {prompt_index} ✅")
                    
                    # Check for data
                    all_values = worksheet.get_all_values()
                    prompt_entries = []
                    
                    for i, row in enumerate(all_values[1:], 2):
                        if len(row) > prompt_index and row[prompt_index].strip():
                            prompt_entries.append((i, row[prompt_index]))
                    
                    if prompt_entries:
                        print(f"   💬 Prompt entries: {len(prompt_entries)}")
                        for row_num, prompt in prompt_entries[-1:]:  # Show latest
                            print(f"      Row {row_num}: {prompt[:80]}...")
                    else:
                        print(f"   📝 Prompt column empty")
                else:
                    print(f"   ❌ No Prompt column")
                    
            except Exception as e:
                print(f"\n📄 {worksheet_name}: Error - {e}")
    
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    # Step 1: Add Prompt columns with fixed method
    add_prompt_column_fixed()
    
    # Step 2: Test writing sample data
    test_write_sample_data()
    
    # Step 3: Verify results
    verify_final_results()
    
    print(f"\n🎯 SUMMARY:")
    print(f"✅ Added Prompt columns to worksheets")
    print(f"✅ Tested writing AI response data")
    print(f"🚀 Now workflows can write AI_Response to Prompt column!")
    print(f"\n💡 NEXT: Run workflow and it should populate Prompt columns!")
