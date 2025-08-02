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


async def debug_node_outputs():
    """Debug the node outputs structure and data flow"""
    
    print("🔍 Debugging Node Outputs Structure...")
    
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
    
    print(f"📊 Node outputs structure:")
    print(f"   Keys: {list(node_outputs.keys())}")
    print(f"   AI output keys: {list(node_outputs['ai-processing-1'].keys())}")
    
    # Test current GoogleSheetsWriteComponent logic
    print(f"\n🧪 Testing GoogleSheetsWriteComponent data detection...")
    
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
        previous_outputs=node_outputs,  # This is what the execution engine passes
        global_variables={}
    )
    
    # Test what the component sees
    print(f"   previous_outputs keys: {list(context.previous_outputs.keys())}")
    print(f"   Looking for 'processed_results': {'processed_results' in context.previous_outputs}")
    print(f"   Looking for 'results_for_sheets': {'results_for_sheets' in context.previous_outputs}")
    
    # The component should look in the actual node outputs
    found_data = None
    for node_id, output_data in context.previous_outputs.items():
        if isinstance(output_data, dict):
            if "processed_results" in output_data:
                found_data = output_data["processed_results"]
                print(f"   ✅ Found 'processed_results' in node '{node_id}'")
                break
            elif "results_for_sheets" in output_data:
                found_data = output_data["results_for_sheets"]
                print(f"   ✅ Found 'results_for_sheets' in node '{node_id}'")
                break
    
    if found_data:
        print(f"   📈 Data found: {len(found_data)} items")
        print(f"   📋 Sample: {found_data[0] if isinstance(found_data, list) and found_data else found_data}")
    else:
        print(f"   ❌ No data found")
    
    print(f"\n🔧 This explains why the component gets 'No data provided to write'")
    print(f"   The component needs to look INSIDE each node's output_data, not at the top level")


if __name__ == "__main__":
    asyncio.run(debug_node_outputs())
