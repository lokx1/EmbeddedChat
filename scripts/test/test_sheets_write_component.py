#!/usr/bin/env python3
"""
Test script để kiểm tra Google Sheets Write component
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from src.services.workflow.component_registry import ComponentRegistry, ExecutionContext, GoogleSheetsWriteComponent

async def test_google_sheets_write():
    """Test Google Sheets Write component với AI response data"""
    
    print("🧪 Testing Google Sheets Write Component...")
    
    # Mock execution context with AI processing results
    mock_previous_outputs = {
        "ai_processing_node": {
            "results_for_sheets": [
                [
                    "Row Index", "Original Description", "Output Format", "Status", 
                    "Generated URL", "Prompt", "Provider", "Model", "Quality", "Size", 
                    "Processing Time", "Timestamp", "Notes"
                ],
                [
                    1, "Design a Task Manager", "PNG", "success",
                    "https://example.com/image1.png", "Create a clean, modern task manager interface with dark theme",
                    "OpenAI", "dall-e-3", "hd", "1024x1024",
                    "2.5s", "2025-01-15 10:30:00", "Generated successfully"
                ],
                [
                    2, "Summer Sale Banner", "JPG", "success", 
                    "https://example.com/image2.jpg", "Design vibrant summer sale banner with 50% OFF text",
                    "Claude", "claude-3", "standard", "1792x1024",
                    "3.1s", "2025-01-15 10:31:00", "High quality output"
                ]
            ]
        }
    }
    
    context = ExecutionContext(
        workflow_id="test-workflow",
        instance_id="test-instance",
        step_id="test-step",
        node_id="test-sheets-write",
        global_variables={},
        input_data={
            "sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",  # Sample Sheet ID
            "sheet_name": "AI_Results",
            "range": "A1",
            "mode": "overwrite",
            "data_format": "auto"
        },
        previous_outputs=mock_previous_outputs
    )
    
    # Test component
    component = GoogleSheetsWriteComponent()
    result = await component.execute(context)
    
    print(f"✅ Execution result:")
    print(f"   Success: {result.success}")
    print(f"   Error: {result.error}")
    print(f"   Execution time: {result.execution_time_ms}ms")
    print(f"   Logs: {result.logs}")
    
    if result.success:
        print("\n📊 Data that would be written to Google Sheets:")
        if "formatted_data" in result.output_data:
            data = result.output_data["formatted_data"]
            for i, row in enumerate(data[:3]):  # Show first 3 rows
                print(f"   Row {i}: {row}")
        
        # Check if Prompt column exists
        if result.output_data.get("formatted_data"):
            headers = result.output_data["formatted_data"][0]
            if "Prompt" in headers:
                prompt_index = headers.index("Prompt")
                print(f"\n🎯 Prompt column found at index {prompt_index}")
                if len(result.output_data["formatted_data"]) > 1:
                    first_prompt = result.output_data["formatted_data"][1][prompt_index]
                    print(f"   First prompt: {first_prompt}")
            else:
                print("\n❌ Prompt column NOT found in headers!")
                print(f"   Available headers: {headers}")
    else:
        print(f"\n❌ Test failed: {result.error}")
    
    return result

async def main():
    """Main test function"""
    print("🔍 Testing Google Sheets Write functionality...\n")
    
    try:
        result = await test_google_sheets_write()
        
        if result.success:
            print("\n✅ All tests passed! Backend is ready to write AI responses to Google Sheets.")
        else:
            print(f"\n❌ Test failed: {result.error}")
            
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
