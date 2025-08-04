#!/usr/bin/env python3
"""
Debug AI Response Write Issue
Check why AI_Response appears in logs but not written to Google Sheets
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Import the components with the correct path
from src.services.workflow.component_registry import AIProcessingComponent, GoogleSheetsWriteComponent
from src.schemas.workflow_components import ExecutionContext

class MockInput:
    def __init__(self, data):
        self.data = data

async def check_credentials():
    """Check if Google Sheets credentials file exists"""
    import os
    
    # Check for credentials in various possible locations
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'credentials.json'),
        os.path.join(os.path.dirname(__file__), 'backend', 'credentials.json'),
        os.path.join(os.path.dirname(__file__), 'backend', 'src', 'credentials.json')
    ]
    
    print("🔐 Checking Google Sheets credentials.json...")
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found credentials at: {path}")
            return True
            
    print("❌ Google Sheets credentials.json not found in expected locations")
    print("⚠️ This will cause API calls to fail and fall back to simulation mode")
    return False

async def debug_ai_response_write():
    """Debug the flow from AI processing to Google Sheets write"""
    print("🔍 DEBUG: AI Response Write Issue")
    print("="*50)
    
    # Check credentials first
    await check_credentials()
    
    # Step 1: Create sample Google Sheets data (like what comes from GoogleSheetsRead)
    print("\n1️⃣ Sample Input Data (from Google Sheets)")
    sheets_data = {
        "records": [
            {
                "Description": "Design a Task Manager app logo",
                "Example Asset URL": "https://example.com/logo.png",
                "Desired Output Format": "PNG",
                "Model Specification": "OpenAI"
            },
            {
                "Description": "Summer Sale banner", 
                "Example Asset URL": "https://example.com/banner.jpg",
                "Desired Output Format": "JPG",
                "Model Specification": "Claude"
            }
        ]
    }
    print(f"   📊 Input records: {len(sheets_data['records'])}")
    for i, record in enumerate(sheets_data['records']):
        print(f"   Record {i+1}: {record['Description']}")
    
    # Step 2: Simulate AI Processing Component
    print("\n2️⃣ AI Processing Component")
    ai_component = AIProcessingComponent()
    
    # Create execution context for AI processing
    ai_context = ExecutionContext(
        workflow_id="debug-workflow",
        instance_id="debug-001",
        step_id="ai-processing-step",
        node_id="ai-processing-node",
        input_data={
            "provider": "ollama",
            "model": "qwen2.5:3b", 
            "prompt_template": "Generate asset for: {input}",
            "temperature": 0.7,
            "max_tokens": 500
        },
        previous_outputs={
            "sheets-read": sheets_data
        },
        global_variables={}
    )
    
    print(f"   🤖 Running AI processing...")
    ai_result = await ai_component.execute(ai_context)
    print(f"   ✅ AI Processing Success: {ai_result.success}")
    
    if ai_result.success:
        print(f"   📊 Output keys: {list(ai_result.output_data.keys())}")
        
        # Check for results_for_sheets
        if "results_for_sheets" in ai_result.output_data:
            results_for_sheets = ai_result.output_data["results_for_sheets"]
            print(f"   🎯 results_for_sheets: {type(results_for_sheets)}")
            print(f"   📝 Header: {results_for_sheets[0] if results_for_sheets else 'None'}")
            print(f"   📝 Rows: {len(results_for_sheets) - 1 if len(results_for_sheets) > 1 else 0}")
            
            # Check for Prompt column
            if results_for_sheets and len(results_for_sheets) > 0:
                headers = results_for_sheets[0]
                if "Prompt" in headers:
                    prompt_index = headers.index("Prompt")
                    print(f"   ⭐ Prompt column found at index {prompt_index}")
                    
                    # Show sample prompt data
                    if len(results_for_sheets) > 1:
                        sample_row = results_for_sheets[1]
                        if len(sample_row) > prompt_index:
                            prompt_text = sample_row[prompt_index]
                            print(f"   📝 Sample prompt: {prompt_text[:100]}...")
                else:
                    print(f"   ❌ Prompt column not found in headers: {headers}")
        else:
            print(f"   ❌ results_for_sheets not found in output")
    
    # Step 3: Simulate Google Sheets Write Component  
    print("\n3️⃣ Google Sheets Write Component")
    sheets_write_component = GoogleSheetsWriteComponent()
    
    # Create execution context for sheets write
    write_context = ExecutionContext(
        workflow_id="debug-workflow",
        instance_id="debug-001",
        step_id="sheets-write-step",
        node_id="sheets-write-node",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": "TEST121",  # Fixed: Set to the specific sheet name mentioned in documentation
            "range": "A1",
            "mode": "overwrite",
            "data_format": "auto"
        },
        previous_outputs={
            "ai-processing": ai_result.output_data if ai_result.success else {}
        },
        global_variables={}
    )
    
    print(f"   📝 Running Google Sheets write...")
    
    try:
        write_result = await sheets_write_component.execute(write_context)
        print(f"   ✅ Write Success: {write_result.success}")
        
        if write_result.success:
            print(f"   📊 Write result: {write_result.output_data}")
            
            # Check if this was a simulation or real API write
            if write_result.output_data and write_result.output_data.get("status") == "simulated":
                print(f"   ⚠️ NOTE: This was a simulated write (Google Sheets API not available)")
                print(f"   ⚠️ To fix: Ensure Google Sheets credentials.json is properly set up")
            
        else:
            print(f"   ❌ Write error: {write_result.error}")
            
    except Exception as e:
        print(f"   💥 Exception during Google Sheets write: {str(e)}")
        import traceback
        print(f"   Stack trace: {traceback.format_exc()}")
        
    # Show logs for debugging
    print(f"\n📋 Write Logs:")
    for log in write_result.logs:
        print(f"   - {log}")
    
    # Step 4: Check data that was prepared for writing
    print("\n4️⃣ Data Analysis")
    
    # Check what data the GoogleSheetsWrite component received
    for node_id, node_output in write_context.previous_outputs.items():
        print(f"   📊 Previous output from {node_id}:")
        if isinstance(node_output, dict):
            for key, value in node_output.items():
                if key == "results_for_sheets" and isinstance(value, list):
                    print(f"      🎯 {key}: {len(value)} rows")
                    if value:
                        print(f"         📝 Headers: {value[0]}")
                        if "Prompt" in value[0]:
                            prompt_col = value[0].index("Prompt")
                            print(f"         ⭐ Prompt column at index {prompt_col}")
                        if len(value) > 1:
                            print(f"         📝 Sample row: {value[1][:6]}...")  # First 6 columns
                else:
                    print(f"      - {key}: {type(value)}")
    
    print(f"\n🎯 SUMMARY")
    print(f"="*30)
    print(f"✅ AI Processing: {ai_result.success}")
    print(f"✅ Sheets Write: {write_result.success}")
    
    if ai_result.success and "results_for_sheets" in ai_result.output_data:
        results = ai_result.output_data["results_for_sheets"]
        if results and "Prompt" in results[0]:
            print(f"✅ Prompt column exists in formatted data")
        else:
            print(f"❌ Prompt column missing from formatted data")
    else:
        print(f"❌ No results_for_sheets generated")
    
    # Step 5: Verification steps for frontend integration
    print(f"\n5️⃣ Frontend Integration Check")
    print(f"="*30)
    print(f"To fully fix the issue in the frontend workflow editor:")
    print(f"1. Open the frontend workflow editor")
    print(f"2. Edit your workflow configuration")
    print(f"3. Ensure Google Sheets Read component has:")
    print(f"   - sheet_id: 1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc")
    print(f"   - sheet_name: TEST121")
    print(f"4. Ensure Google Sheets Write component has:")
    print(f"   - sheet_id: 1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc")
    print(f"   - sheet_name: TEST121")
    print(f"5. Save and execute the workflow")
    print(f"6. Verify that the AI responses appear in the Prompt column")

if __name__ == "__main__":
    asyncio.run(debug_ai_response_write())
