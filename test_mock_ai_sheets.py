#!/usr/bin/env python3
"""
Simple debug script to test Google Sheets Write with mock AI data
This bypasses the AI processing to focus on the sheets writing issue
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Import the components with the correct path
from src.services.workflow.component_registry import GoogleSheetsWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def test_sheets_write_with_mock_ai_data():
    """Test Google Sheets Write with mock AI data that includes Prompt column"""
    print("🔍 SIMPLE DEBUG: Google Sheets Write with Mock AI Data")
    print("="*60)
    
    # Create mock AI processing output that includes the Prompt column
    mock_ai_output = {
        "results_for_sheets": [
            # Header row with Prompt column
            ["Row Index", "Original Description", "Output Format", "Status", "Generated URL", "Prompt", "Provider", "Model"],
            # Data rows with AI responses in Prompt column
            [1, "Design a Task Manager app logo", "PNG", "success", "https://demo-assets.local/png/1234.png", 
             "Create a modern, minimalist task manager logo with clean lines and professional appearance. Use blue and gray colors for a tech-focused look.", 
             "ollama", "qwen2.5:3b"],
            [2, "Summer Sale banner", "JPG", "success", "https://demo-assets.local/jpg/5678.jpg", 
             "Design a vibrant summer sale banner with tropical elements, bright colors, and clear promotional text. Include palm leaves and sunset gradients.", 
             "ollama", "qwen2.5:3b"]
        ],
        "processed_results": [
            {
                "row_index": 1,
                "input_data": {"description": "Design a Task Manager app logo", "output_format": "PNG"},
                "ai_response": {"generated_url": "https://demo-assets.local/png/1234.png", "ai_response": "Create a modern, minimalist task manager logo..."},
                "status": "success"
            },
            {
                "row_index": 2,
                "input_data": {"description": "Summer Sale banner", "output_format": "JPG"},
                "ai_response": {"generated_url": "https://demo-assets.local/jpg/5678.jpg", "ai_response": "Design a vibrant summer sale banner..."},
                "status": "success"
            }
        ]
    }
    
    print(f"📊 Mock AI Data Created:")
    print(f"   - results_for_sheets: {len(mock_ai_output['results_for_sheets'])} rows")
    print(f"   - Headers: {mock_ai_output['results_for_sheets'][0]}")
    print(f"   - Prompt column at index: {mock_ai_output['results_for_sheets'][0].index('Prompt')}")
    
    # Test Google Sheets Write Component
    print(f"\n📝 Testing Google Sheets Write Component...")
    sheets_write_component = GoogleSheetsWriteComponent()
    
    # Create execution context for sheets write
    write_context = ExecutionContext(
        workflow_id="debug-workflow",
        instance_id="debug-simple-001",
        step_id="sheets-write-step",
        node_id="sheets-write-node",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": "TEST121",  # Use the specific sheet name from documentation
            "range": "A1",
            "mode": "overwrite",
            "data_format": "auto"
        },
        previous_outputs={
            "ai-processing": mock_ai_output  # Provide the mock AI data
        },
        global_variables={}
    )
    
    try:
        print(f"   🚀 Executing Google Sheets Write...")
        write_result = await sheets_write_component.execute(write_context)
        
        print(f"   ✅ Write Success: {write_result.success}")
        
        if write_result.success:
            print(f"   📊 Write result: {write_result.output_data}")
            
            # Check if this was a simulation or real API write
            if write_result.output_data and write_result.output_data.get("status") == "simulated":
                print(f"   ⚠️ NOTE: This was a simulated write (Google Sheets API not available)")
                print(f"   ⚠️ To enable real writes: Ensure Google Sheets credentials.json is properly configured")
            elif write_result.output_data and write_result.output_data.get("status") == "success":
                print(f"   🎉 SUCCESS: Real write to Google Sheets completed!")
                print(f"   📋 Check the TEST121 worksheet for the AI responses in the Prompt column")
            
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
    
    # Analyze the data that was processed
    print(f"\n🔍 Data Analysis:")
    print(f"   📊 Input data keys: {list(write_context.input_data.keys())}")
    print(f"   📊 Previous outputs: {list(write_context.previous_outputs.keys())}")
    
    if "ai-processing" in write_context.previous_outputs:
        ai_data = write_context.previous_outputs["ai-processing"]
        if "results_for_sheets" in ai_data:
            results = ai_data["results_for_sheets"]
            print(f"   ✅ Found results_for_sheets with {len(results)} rows")
            if results and "Prompt" in results[0]:
                prompt_index = results[0].index("Prompt")
                print(f"   ✅ Prompt column found at index {prompt_index}")
                if len(results) > 1:
                    sample_prompt = results[1][prompt_index]
                    print(f"   📝 Sample prompt: {sample_prompt[:50]}...")
            else:
                print(f"   ❌ Prompt column not found in headers")
    
    print(f"\n🎯 SUMMARY")
    print(f"="*30)
    print(f"✅ Mock AI Data: Created successfully")
    print(f"✅ Sheets Write: {write_result.success}")
    
    if write_result.success:
        if write_result.output_data and write_result.output_data.get("status") == "success":
            print(f"🎉 RESULT: AI responses should now be visible in Google Sheets TEST121 worksheet!")
            print(f"📋 The Prompt column should contain the cleaned AI responses")
        else:
            print(f"⚠️ RESULT: Write completed but in simulation mode")
            print(f"📋 Check Google Sheets credentials to enable real API writes")
    else:
        print(f"❌ RESULT: Write failed - check error logs above")

if __name__ == "__main__":
    asyncio.run(test_sheets_write_with_mock_ai_data())
