#!/usr/bin/env python3
"""
Test Google Drive Write Component
"""
import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.workflow.component_registry import GoogleDriveWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def test_google_drive_write():
    """Test Google Drive Write Component"""
    
    print("=== Google Drive Write Component Test ===")
    
    # Get component metadata
    component = GoogleDriveWriteComponent()
    metadata = component.get_metadata()
    
    print(f"Component Type: {metadata.type}")
    print(f"Component Name: {metadata.name}")
    print(f"Description: {metadata.description}")
    print(f"Category: {metadata.category}")
    print()
    
    # Test 1: Upload JSON data
    print("Test 1: Upload JSON data")
    test_data = {
        "users": [
            {"name": "John Doe", "email": "john@example.com", "age": 30},
            {"name": "Jane Smith", "email": "jane@example.com", "age": 25}
        ],
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    context = ExecutionContext(
        workflow_id="test-workflow",
        workflow_instance_id="test-instance",
        step_id="test-step",
        input_data={
            "file_name": "test_users.json",
            "folder_id": "",  # Root folder
            "file_type": "json",
            "content_source": "previous_output"
        },
        previous_outputs={
            "data_node": {
                "data": test_data
            }
        }
    )
    
    result = await component.execute(context)
    
    print(f"Success: {result.success}")
    print(f"Execution time: {result.execution_time_ms}ms")
    if result.success:
        print(f"Output data: {result.output_data}")
    else:
        print(f"Error: {result.error}")
    
    print("\nLogs:")
    for log in result.logs:
        print(f"  - {log}")
    print()
    
    # Test 2: Upload CSV data
    print("Test 2: Upload CSV data")
    csv_data = [
        {"Name": "Product A", "Price": 100, "Stock": 50},
        {"Name": "Product B", "Price": 200, "Stock": 30},
        {"Name": "Product C", "Price": 150, "Stock": 20}
    ]
    
    context2 = ExecutionContext(
        workflow_id="test-workflow",
        workflow_instance_id="test-instance",
        step_id="test-step",
        input_data={
            "file_name": "products.csv",
            "folder_id": "",
            "file_type": "csv",
            "content_source": "previous_output"
        },
        previous_outputs={
            "csv_node": {
                "records": csv_data
            }
        }
    )
    
    result2 = await component.execute(context2)
    
    print(f"Success: {result2.success}")
    print(f"Execution time: {result2.execution_time_ms}ms")
    if result2.success:
        print(f"Output data: {result2.output_data}")
    else:
        print(f"Error: {result2.error}")
    
    print("\nLogs:")
    for log in result2.logs:
        print(f"  - {log}")
    print()
    
    # Test 3: Upload text data
    print("Test 3: Upload text data")
    text_data = """This is a test document.

It contains multiple lines of text.
It can be used to test the Google Drive Write component.

Created: 2024-01-15
"""
    
    context3 = ExecutionContext(
        workflow_id="test-workflow",
        workflow_instance_id="test-instance",
        step_id="test-step",
        input_data={
            "file_name": "test_document.txt",
            "folder_id": "",
            "file_type": "text",
            "content_source": "input_data",
            "content_data": text_data
        },
        previous_outputs={}
    )
    
    result3 = await component.execute(context3)
    
    print(f"Success: {result3.success}")
    print(f"Execution time: {result3.execution_time_ms}ms")
    if result3.success:
        print(f"Output data: {result3.output_data}")
    else:
        print(f"Error: {result3.error}")
    
    print("\nLogs:")
    for log in result3.logs:
        print(f"  - {log}")
    print()
    
    # Test 4: Error case - no content
    print("Test 4: Error case - no content")
    context4 = ExecutionContext(
        workflow_id="test-workflow",
        workflow_instance_id="test-instance",
        step_id="test-step",
        input_data={
            "file_name": "empty_file.txt",
            "folder_id": "",
            "file_type": "text",
            "content_source": "previous_output"
        },
        previous_outputs={}
    )
    
    result4 = await component.execute(context4)
    
    print(f"Success: {result4.success}")
    if not result4.success:
        print(f"Error: {result4.error}")
    
    print("\nLogs:")
    for log in result4.logs:
        print(f"  - {log}")

if __name__ == "__main__":
    asyncio.run(test_google_drive_write())
