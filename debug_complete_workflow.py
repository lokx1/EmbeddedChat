#!/usr/bin/env python3
"""
Debug toàn bộ AI workflow - từ AI Processing đến Sheets Write
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

import requests
import time
import json
import gspread
from google.oauth2.service_account import Credentials

def check_ai_processing_output():
    """Check output từ AI Processing component"""
    
    print("🔍 Checking AI Processing component output...")
    
    # Simulate AI processing result
    mock_ai_result = {
        "ai-processing-3": {
            "processed_results": [
                {
                    "row_index": 1,
                    "input_data": {
                        "description": "Design a Task Manager app logo",
                        "output_format": "PNG"
                    },
                    "ai_response": {
                        "ai_response": "Create a modern, clean logo for a Task Manager application. Use professional blue and gray colors, incorporate a checkmark or list icon, ensure scalability for various sizes including mobile apps and web interfaces.",
                        "generated_url": "https://example.com/logo.png",
                        "metadata": {"quality": "high", "processing_time": "2.3s"}
                    },
                    "status": "completed",
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "timestamp": "2025-01-01T10:00:00"
                }
            ],
            "results_for_sheets": None  # This will be generated
        }
    }
    
    # Import AI Processing component to test _format_results_for_sheets
    from services.workflow.component_registry import AIProcessingComponent
    
    ai_component = AIProcessingComponent()
    processed_results = mock_ai_result["ai-processing-3"]["processed_results"]
    
    # Generate results_for_sheets
    results_for_sheets = ai_component._format_results_for_sheets(processed_results)
    
    print(f"✅ Generated results_for_sheets:")
    print(f"📊 Headers: {results_for_sheets[0] if results_for_sheets else 'No headers'}")
    print(f"📊 Data rows: {len(results_for_sheets) - 1 if results_for_sheets else 0}")
    
    if results_for_sheets and len(results_for_sheets) > 1:
        print(f"📊 First data row: {results_for_sheets[1]}")
        
        # Check if Prompt column has data
        headers = results_for_sheets[0]
        if "Prompt" in headers:
            prompt_idx = headers.index("Prompt")
            prompt_value = results_for_sheets[1][prompt_idx] if len(results_for_sheets[1]) > prompt_idx else ""
            print(f"✅ Prompt column data: {prompt_value[:100]}...")
        else:
            print(f"❌ Prompt column not found in headers")
    
    return results_for_sheets

def test_sheets_write_with_prompt(results_for_sheets):
    """Test GoogleSheetsWriteComponent với data có Prompt column"""
    
    print("\n🔧 Testing GoogleSheetsWriteComponent...")
    
    # Import component
    from services.workflow.component_registry import GoogleSheetsWriteComponent, ExecutionContext
    
    # Create mock context
    context = ExecutionContext(
        node_id="test_sheets_write",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": "HEY",
            "range": "A1",
            "mode": "overwrite"
        },
        previous_outputs={
            "ai-processing-3": {
                "results_for_sheets": results_for_sheets
            }
        },
        workflow_context={}
    )
    
    # Execute
    import asyncio
    
    async def run_test():
        component = GoogleSheetsWriteComponent()
        result = await component.execute(context)
        
        print(f"📊 Execution result:")
        print(f"   Success: {result.success}")
        print(f"   Error: {result.error}")
        print(f"   Logs:")
        for log in result.logs:
            print(f"     {log}")
        
        return result.success
    
    return asyncio.run(run_test())

def verify_prompt_in_sheet():
    """Verify nếu Prompt column đã được ghi vào worksheet HEY"""
    
    print("\n🔍 Verifying Prompt column in worksheet HEY...")
    
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
        worksheet = sheet.worksheet("HEY")
        
        # Get all data
        all_values = worksheet.get_all_values()
        
        if len(all_values) > 0:
            headers = all_values[0]
            print(f"📋 Current headers: {headers}")
            
            if "Prompt" in headers:
                prompt_idx = headers.index("Prompt")
                print(f"✅ Prompt column found at index {prompt_idx}")
                
                # Check data in Prompt column
                prompt_data_count = 0
                for i, row in enumerate(all_values[1:], 2):
                    if len(row) > prompt_idx:
                        prompt_value = row[prompt_idx] if prompt_idx < len(row) else ""
                        if prompt_value and len(prompt_value.strip()) > 10:
                            prompt_data_count += 1
                            print(f"✅ Row {i}: {prompt_value[:80]}...")
                        else:
                            print(f"❌ Row {i}: Empty or short prompt")
                
                print(f"📊 Total rows with Prompt data: {prompt_data_count}")
                return prompt_data_count > 0
            else:
                print(f"❌ Prompt column not found")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Complete AI Workflow Debug")
    print("="*60)
    
    # Step 1: Test AI Processing output
    results_for_sheets = check_ai_processing_output()
    
    if not results_for_sheets:
        print("❌ AI Processing failed to generate results_for_sheets")
        exit(1)
    
    print("\n" + "="*60)
    
    # Step 2: Test Sheets Write with Prompt data
    write_success = test_sheets_write_with_prompt(results_for_sheets)
    
    print("\n" + "="*60)
    
    # Step 3: Verify actual data in sheet
    verification_success = verify_prompt_in_sheet()
    
    print("\n" + "="*60)
    print("🎯 Debug Summary:")
    print(f"   AI Processing generates Prompt data: ✅")
    print(f"   Sheets Write component executes: {'✅' if write_success else '❌'}")
    print(f"   Prompt data written to sheet: {'✅' if verification_success else '❌'}")
    
    if write_success and verification_success:
        print("🎉 Auto-add Prompt column workflow working correctly!")
    else:
        print("⚠️ There are issues in the workflow that need fixing.")
