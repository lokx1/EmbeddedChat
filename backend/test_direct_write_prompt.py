#!/usr/bin/env python3
"""
Direct test of GoogleSheetsWriteComponent with auto-add Prompt feature
"""

import sys
import os
import asyncio

# Add src to path
sys.path.append('src')

from services.workflow.component_registry import GoogleSheetsWriteComponent
from services.workflow.types import ExecutionContext, ComponentInput

async def test_direct_write_with_prompt():
    """Test GoogleSheetsWriteComponent directly with Prompt column data"""
    print("🚀 DIRECT TEST - GOOGLE SHEETS WRITE WITH PROMPT")
    print("="*55)
    
    # Create component instance
    component = GoogleSheetsWriteComponent()
    
    # Test data with Prompt column (simulating AI processing output)
    test_data_with_prompt = [
        ["Row Index", "Original Description", "Output Format", "Status", "Generated URL", "Prompt", "Provider", "Model"],
        [1, "Create a logo", "PNG", "success", "https://example.com/logo.png", "Create a detailed and comprehensive prompt for generating a Task Manager app logo. The logo should be modern, clean, and professional with a focus on productivity and efficiency.", "openai", "gpt-3.5-turbo"],
        [2, "Design icon", "SVG", "success", "https://example.com/icon.svg", "Design a settings icon that is intuitive and follows modern UI guidelines. The icon should be recognizable and work well at small sizes.", "openai", "gpt-3.5-turbo"]
    ]
    
    # Prepare execution context
    context = ExecutionContext(
        instance_id="test_auto_prompt_123",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "worksheet_name": "YES",  # Target worksheet without Prompt column
            "range": "A1",
            "mode": "overwrite",
            "data_format": "auto"
        },
        previous_outputs={
            "ai_processing": {
                "results_for_sheets": test_data_with_prompt
            }
        }
    )
    
    print(f"📋 Target worksheet: YES")
    print(f"📊 Test data: {len(test_data_with_prompt)} rows")
    print(f"📊 Headers: {test_data_with_prompt[0]}")
    print(f"🎯 Prompt column included: {'Prompt' in test_data_with_prompt[0]}")
    
    try:
        # Execute the component
        print(f"\n🚀 Executing GoogleSheetsWriteComponent...")
        result = await component.execute(context)
        
        print(f"\n📊 EXECUTION RESULTS:")
        print(f"   Success: {result.success}")
        print(f"   Execution time: {result.execution_time_ms}ms")
        
        if result.success:
            output = result.output_data
            print(f"   📝 Operation: {output.get('operation', 'N/A')}")
            print(f"   📊 Status: {output.get('status', 'N/A')}")
            
            if 'data_written' in output:
                data_written = output['data_written']
                print(f"   📊 Rows written: {data_written.get('rows_count', 0)}")
                print(f"   📊 Columns written: {data_written.get('columns_count', 0)}")
                print(f"   📍 Range written: {data_written.get('range_written', 'N/A')}")
        else:
            print(f"   ❌ Error: {result.error}")
        
        # Show relevant logs
        print(f"\n📋 EXECUTION LOGS:")
        if result.logs:
            for log in result.logs:
                if any(keyword in log for keyword in [
                    'Prompt', 'headers', 'Adding', 'Added', 'Auto', 'worksheet_name', 'write'
                ]):
                    print(f"   🎯 {log}")
        
        return result.success
        
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")
        return False

async def verify_worksheet_after_test():
    """Verify the worksheet after direct test"""
    print(f"\n🔍 VERIFYING WORKSHEET AFTER TEST")
    print("="*35)
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Set up credentials
        credentials_path = "credentials.json"
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet = client.open_by_key(sheet_id)
        
        # Check YES worksheet
        worksheet = sheet.worksheet("YES")
        
        # Get current state
        headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
        all_values = worksheet.get_all_values()
        
        print(f"📄 YES worksheet:")
        print(f"   Headers: {headers}")
        print(f"   Total rows: {len(all_values)}")
        
        if "Prompt" in headers:
            prompt_index = headers.index("Prompt")
            print(f"   🎯 Prompt column at index {prompt_index} ✅")
            
            # Check for data in Prompt column
            prompt_entries = []
            for i, row in enumerate(all_values[1:], 2):  # Start from row 2
                if len(row) > prompt_index and row[prompt_index].strip():
                    prompt_entries.append((i, row[prompt_index]))
            
            print(f"   💬 Prompt entries: {len(prompt_entries)}")
            
            if prompt_entries:
                for row_num, prompt in prompt_entries[-2:]:  # Show last 2
                    print(f"      Row {row_num}: {prompt[:80]}...")
            else:
                print(f"   📝 Prompt column exists but no data")
        else:
            print(f"   ❌ No Prompt column found")
    
    except Exception as e:
        print(f"💥 Error verifying: {e}")

async def main():
    success = await test_direct_write_with_prompt()
    await verify_worksheet_after_test()
    
    if success:
        print(f"\n✅ Direct test completed successfully")
        print(f"🎯 Check YES worksheet for Prompt column and data")
    else:
        print(f"\n❌ Direct test failed")

if __name__ == "__main__":
    asyncio.run(main())
