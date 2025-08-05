#!/usr/bin/env python3
"""
Fix Workflow: AI Processing → Google Sheets Write
Fix vấn đề AI output không được ghi vào Google Sheets
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.services.workflow.component_registry import GoogleSheetsComponent, AIProcessingComponent, GoogleSheetsWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def test_ai_to_sheets_workflow():
    """Test complete AI processing to Google Sheets workflow"""
    print("🔧 FIXING: AI Processing → Google Sheets Write")
    print("="*60)
    
    # Step 1: Read from Google Sheets
    print("\n📊 Step 1: Reading data from Google Sheets...")
    sheets_component = GoogleSheetsComponent()
    
    sheets_context = ExecutionContext(
        workflow_id="fix-workflow",
        instance_id="fix-instance-001",
        step_id="sheets-read",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": "Sheet1",
            "range": "A1:F10",  # Limit to first 10 rows for testing
            "output_format": "records"
        },
        previous_outputs={},
        global_variables={}
    )
    
    sheets_result = await sheets_component.execute(sheets_context)
    
    if not sheets_result.success:
        print(f"❌ Failed to read from Google Sheets: {sheets_result.error}")
        return False
    
    print(f"✅ Read {len(sheets_result.output_data.get('records', []))} records from Google Sheets")
    
    # Step 2: Process with AI
    print("\n🤖 Step 2: Processing with AI...")
    ai_component = AIProcessingComponent()
    
    ai_context = ExecutionContext(
        workflow_id="fix-workflow", 
        instance_id="fix-instance-001",
        step_id="ai-processing",
        input_data={
            "provider": "ollama",
            "model": "qwen2.5:3b",
            "prompt": "Create a detailed asset specification for: {description}. Format: Output type should be {output_format}. Provide technical details and implementation notes.",
            "temperature": 0.3,
            "max_tokens": 200
        },
        previous_outputs={
            "sheets-read": sheets_result.output_data
        },
        global_variables={}
    )
    
    ai_result = await ai_component.execute(ai_context)
    
    if not ai_result.success:
        print(f"❌ Failed AI processing: {ai_result.error}")
        return False
    
    print(f"✅ AI processed {len(ai_result.output_data.get('processed_results', []))} records")
    print(f"📋 AI created {len(ai_result.output_data.get('results_for_sheets', []))} rows for sheets")
    
    # Step 3: Write AI results back to Google Sheets (NEW SHEET)
    print("\n📝 Step 3: Writing AI results to Google Sheets...")
    sheets_write_component = GoogleSheetsWriteComponent()
    
    # Create a new sheet name with timestamp
    results_sheet_name = f"AI_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    sheets_write_context = ExecutionContext(
        workflow_id="fix-workflow",
        instance_id="fix-instance-001", 
        step_id="sheets-write",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": results_sheet_name,  # Write to new sheet
            "range": "A1",
            "mode": "overwrite",
            "data_format": "auto"
        },
        previous_outputs={
            "ai-processing": ai_result.output_data
        },
        global_variables={}
    )
    
    sheets_write_result = await sheets_write_component.execute(sheets_write_context)
    
    if sheets_write_result.success:
        print(f"✅ Successfully wrote AI results to Google Sheets!")
        print(f"📊 Sheet: {results_sheet_name}")
        print(f"🔗 View: https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit")
        
        # Show write details
        output_data = sheets_write_result.output_data
        if 'data_written' in output_data:
            data_written = output_data['data_written']
            print(f"📝 Rows written: {data_written.get('rows_count', 'N/A')}")
            print(f"📊 Columns written: {data_written.get('columns_count', 'N/A')}")
        
        return True
    else:
        print(f"❌ Failed to write to Google Sheets: {sheets_write_result.error}")
        print("📝 Logs:")
        for log in sheets_write_result.logs:
            print(f"  - {log}")
        return False

async def fix_sheets_write_component():
    """Fix the Google Sheets Write component to handle AI data properly"""
    print("\n🔧 FIXING: Google Sheets Write Component")
    print("="*50)
    
    # Test sample AI data structure
    sample_ai_data = {
        "processed_results": [
            {
                "row_index": 1,
                "input_data": {"description": "Design a Task Manager app logo", "output_format": "PNG"},
                "ai_response": {"generated_url": "https://ollama-assets.local/png/1234.png"},
                "status": "success"
            }
        ],
        "results_for_sheets": [
            ["Row Index", "Original Description", "Output Format", "Status", "Generated URL", "Provider", "Model"],
            [1, "Design a Task Manager app logo", "PNG", "success", "https://ollama-assets.local/png/1234.png", "ollama", "qwen2.5:3b"]
        ],
        "summary": {
            "total_records": 1,
            "processed_records": 1,
            "successful_records": 1
        }
    }
    
    sheets_write_component = GoogleSheetsWriteComponent()
    
    # Test writing AI data directly
    direct_context = ExecutionContext(
        workflow_id="fix-test",
        instance_id="fix-test-001",
        step_id="direct-write",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": f"Test_Fix_{datetime.now().strftime('%H%M%S')}",
            "range": "A1",
            "mode": "overwrite",
            "data_format": "auto",
            "input_data": sample_ai_data  # Direct data input
        },
        previous_outputs={},
        global_variables={}
    )
    
    result = await sheets_write_component.execute(direct_context)
    
    if result.success:
        print("✅ Direct AI data write test PASSED")
        return True
    else:
        print(f"❌ Direct AI data write test FAILED: {result.error}")
        print("📝 Logs:")
        for log in result.logs:
            print(f"  - {log}")
        return False

async def main():
    """Main test function"""
    print("🚀 WORKFLOW AI → SHEETS WRITE FIX")
    print("="*70)
    
    # Test 1: Direct component fix
    print("\n📋 Test 1: Google Sheets Write Component Fix")
    fix_success = await fix_sheets_write_component()
    
    if not fix_success:
        print("\n❌ Component fix failed, stopping here")
        return
    
    # Test 2: Full workflow test
    print("\n📋 Test 2: Complete AI → Sheets Workflow")
    workflow_success = await test_ai_to_sheets_workflow()
    
    if workflow_success:
        print("\n🎉 WORKFLOW FIX COMPLETED SUCCESSFULLY!")
        print("\n📋 Summary:")
        print("✅ AI Processing Component working")
        print("✅ Google Sheets Write Component fixed")
        print("✅ AI results now written to Google Sheets")
        print("✅ New sheet created with AI outputs")
        
        print("\n🎯 Next Steps:")
        print("1. Check the new AI_Results sheet in your Google Sheets")
        print("2. The workflow now properly writes AI outputs")
        print("3. Each AI processing run creates a new results sheet")
    else:
        print("\n❌ Workflow fix failed")
        print("🔍 Check the logs above for specific errors")

if __name__ == "__main__":
    asyncio.run(main())
