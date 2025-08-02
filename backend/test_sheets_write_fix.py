#!/usr/bin/env python3

import asyncio
import sys
import os
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Simple data classes for testing
class ExecutionContext:
    def __init__(self, workflow_id, instance_id, step_id, input_data, previous_outputs, global_variables):
        self.workflow_id = workflow_id
        self.instance_id = instance_id
        self.step_id = step_id
        self.input_data = input_data
        self.previous_outputs = previous_outputs
        self.global_variables = global_variables


async def test_sheets_write_fix():
    """Test the fixed GoogleSheetsWriteComponent"""
    
    print("🧪 Testing Fixed GoogleSheetsWriteComponent...")
    
    # Import here to avoid circular import issues
    from services.workflow.component_registry import GoogleSheetsWriteComponent
    
    # Simulate AI Processing output (like what would be stored in node_outputs)
    ai_output_data = {
        "processed_results": [
            {
                "row_index": 1,
                "input_data": {"description": "Test image", "output_format": "PNG"},
                "ai_response": {"generated_url": "https://example.com/test.png"},
                "status": "success",
                "provider": "ollama",
                "model": "qwen3:8b"
            }
        ],
        "summary": {
            "total_records": 1,
            "processed_records": 1,
            "successful_records": 1
        },
        "results_for_sheets": [
            ["Row Index", "Original Description", "Output Format", "Status", "Generated URL"],
            [1, "Test image", "PNG", "success", "https://example.com/test.png"]
        ]
    }
    
    # This is how the execution engine stores outputs: {node_id: output_data}
    node_outputs = {
        "ai-processing-1": ai_output_data,
        "sheets-read-1": {
            "values": [["description", "output_format"], ["Test image", "PNG"]],
            "spreadsheet_info": {"title": "Test Sheet"}
        }
    }
    
    # Create context as execution engine would
    context = ExecutionContext(
        workflow_id="test",
        instance_id="test",
        step_id="sheets-write-4",
        input_data={
            "sheet_id": "1WjySc8DxYoPJf3gJtyPXUJpRfdFza",
            "sheet_name": "Test",
            "range": "A1",
            "mode": "append",
            "data_format": "auto"
        },
        previous_outputs=node_outputs,
        global_variables={}
    )
    
    # Test the component
    component = GoogleSheetsWriteComponent()
    print(f"📋 Executing GoogleSheetsWriteComponent...")
    
    try:
        result = await component.execute(context)
        print(f"✅ Success: {result.success}")
        print(f"📊 Output: {result.output_data}")
        print(f"📝 Logs: {result.logs}")
        if not result.success:
            print(f"❌ Error: {result.error}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_sheets_write_fix())
