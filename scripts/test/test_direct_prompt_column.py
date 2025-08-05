#!/usr/bin/env python3
"""
Direct test of auto-add Prompt column in GoogleSheetsService
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.workflow.google_services import GoogleSheetsService

async def test_auto_prompt_column_direct():
    """Test auto-add Prompt column directly"""
    print("🚀 DIRECT TEST - AUTO-ADD PROMPT COLUMN")
    print("="*50)
    
    # Initialize service
    credentials_path = os.path.join("backend", "credentials.json")
    service = GoogleSheetsService(credentials_path)
    
    # Authenticate
    print("🔑 Authenticating...")
    auth_success = await service.authenticate()
    
    if not auth_success:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Test data with Prompt column
    test_data = [
        ["Row Index", "Original Description", "Output Format", "Status", "Generated URL", "Prompt", "Provider", "Model"],
        [1, "Create a logo for Task Manager app", "PNG", "success", "https://example.com/logo.png", "Create a detailed and comprehensive prompt for a Task Manager app logo. The logo should be modern, clean, and professional...", "openai", "gpt-3.5-turbo"],
        [2, "Design icon for Settings", "SVG", "success", "https://example.com/settings.svg", "Design a settings icon that is intuitive and follows modern UI guidelines...", "openai", "gpt-3.5-turbo"]
    ]
    
    # Target sheet and worksheets to test
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    test_worksheets = [
        "TEST121",      # Existing worksheet without Prompt column
        "YES",          # Another existing worksheet
        "AUTO_PROMPT_TEST"  # New worksheet (will be created)
    ]
    
    for worksheet_name in test_worksheets:
        print(f"\n🔸 Testing worksheet: {worksheet_name}")
        print("-" * 30)
        
        try:
            # Test the write_to_sheet method
            success, result = await service.write_to_sheet(
                sheet_id=sheet_id,
                sheet_name=worksheet_name,
                range_start="A1",
                mode="overwrite",
                data=test_data
            )
            
            print(f"📝 Write result: {'✅ Success' if success else '❌ Failed'}")
            
            if success:
                data_written = result.get('data_written', {})
                rows_count = data_written.get('rows_count', 0)
                columns_count = data_written.get('columns_count', 0)
                range_written = data_written.get('range_written', 'N/A')
                
                print(f"   📊 Rows written: {rows_count}")
                print(f"   📊 Columns written: {columns_count}")
                print(f"   📍 Range: {range_written}")
                print(f"   🎯 Status: {result.get('status', 'Unknown')}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Error testing {worksheet_name}: {e}")

async def verify_results():
    """Verify the results by reading the worksheets"""
    print(f"\n🔍 VERIFYING RESULTS")
    print("="*25)
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Set up credentials
        credentials_path = os.path.join("backend", "credentials.json")
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet = client.open_by_key(sheet_id)
        
        test_worksheets = ["TEST121", "YES", "AUTO_PROMPT_TEST"]
        
        for worksheet_name in test_worksheets:
            try:
                worksheet = sheet.worksheet(worksheet_name)
                
                # Get headers
                headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
                
                print(f"\n📄 {worksheet_name}:")
                print(f"   Headers: {headers}")
                
                if "Prompt" in headers:
                    prompt_col_index = headers.index("Prompt")
                    print(f"   🎯 Prompt column at index {prompt_col_index}")
                    
                    # Check for data in Prompt column
                    all_values = worksheet.get_all_values()
                    
                    if len(all_values) > 1:  # Has data beyond headers
                        # Check last few rows for Prompt data
                        for i in range(max(1, len(all_values) - 3), len(all_values)):
                            row = all_values[i]
                            if len(row) > prompt_col_index and row[prompt_col_index].strip():
                                print(f"      Row {i+1}: {row[prompt_col_index][:60]}...")
                    else:
                        print(f"   📝 Only headers, no data rows")
                else:
                    print(f"   ❌ No Prompt column found")
                    
            except gspread.WorksheetNotFound:
                print(f"\n📄 {worksheet_name}: Not found (may not have been created)")
            except Exception as e:
                print(f"\n📄 {worksheet_name}: Error - {e}")
    
    except Exception as e:
        print(f"💥 Error verifying: {e}")

async def main():
    await test_auto_prompt_column_direct()
    await verify_results()
    
    print(f"\n💡 SUMMARY:")
    print(f"✅ Tested auto-add Prompt column feature")
    print(f"📝 Should create/update worksheets with Prompt column")
    print(f"🎯 AI_Response data should be written to Prompt column")

if __name__ == "__main__":
    asyncio.run(main())
