#!/usr/bin/env python3
"""
Test Google Drive Write Component with data from Google Sheets
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.workflow.component_registry import GoogleSheetsComponent, GoogleDriveWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def test_sheets_to_drive_workflow():
    """Test reading from Google Sheets and writing to Google Drive"""
    
    print("=== Sheets to Drive Integration Test ===")
    
    # Step 1: Read data from Google Sheets
    print("\n📊 Step 1: Reading data from Google Sheets...")
    
    sheets_component = GoogleSheetsComponent()
    
    # Context for reading from the provided sheet
    sheets_context = ExecutionContext(
        workflow_id="test-workflow",
        instance_id="test-instance-001",
        step_id="sheets-read",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": "Sheet1",
            "range": "A:Z",  # Read all columns
            "output_format": "records"  # Get as list of dictionaries
        },
        previous_outputs={},
        global_variables={}
    )
    
    sheets_result = await sheets_component.execute(sheets_context)
    
    print(f"Sheets read success: {sheets_result.success}")
    if sheets_result.success:
        print(f"Data retrieved: {len(sheets_result.output_data.get('data', []))} rows")
        print("Sample data:", sheets_result.output_data.get('data', [])[:3])  # Show first 3 rows
    else:
        print(f"Sheets read error: {sheets_result.error}")
        return False
    
    # Step 2: Prepare file names with date
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Test scenarios for different file types
    test_scenarios = [
        {
            "file_name": f"Result_{current_date}.json",
            "file_type": "json",
            "description": "JSON format"
        },
        {
            "file_name": f"Result_{current_date}.csv", 
            "file_type": "csv",
            "description": "CSV format"
        },
        {
            "file_name": f"Result_Summary_{current_date}.txt",
            "file_type": "text", 
            "description": "Text summary"
        }
    ]
    
    drive_component = GoogleDriveWriteComponent()
    
    for scenario in test_scenarios:
        print(f"\n📁 Step 2: Uploading to Google Drive - {scenario['description']}")
        
        # Context for writing to Google Drive
        drive_context = ExecutionContext(
            workflow_id="test-workflow",
            instance_id="test-instance-001",
            step_id="drive-write",
            input_data={
                "file_name": scenario["file_name"],
                "folder_id": "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182",  # Your provided folder ID
                "file_type": scenario["file_type"],
                "content_source": "previous_output",
                "mimetype": ""
            },
            previous_outputs={
                "sheets_node": {
                    "data": sheets_result.output_data.get('data', [])
                }
            },
            global_variables={}
        )
        
        drive_result = await drive_component.execute(drive_context)
        
        print(f"Drive upload success: {drive_result.success}")
        if drive_result.success:
            print(f"File uploaded: {scenario['file_name']}")
            print(f"Operation details: {drive_result.output_data}")
        else:
            print(f"Drive upload error: {drive_result.error}")
        
        print(f"Execution time: {drive_result.execution_time_ms}ms")
        print("Logs:")
        for log in drive_result.logs:
            print(f"  - {log}")
        print("-" * 50)

async def test_file_name_logic():
    """Test the file naming logic with conflict detection"""
    
    print("\n=== File Naming Logic Test ===")
    
    drive_component = GoogleDriveWriteComponent()
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Test data
    test_data = [
        {"Name": "Test User 1", "Email": "test1@example.com", "Status": "Active"},
        {"Name": "Test User 2", "Email": "test2@example.com", "Status": "Pending"},
        {"Name": "Test User 3", "Email": "test3@example.com", "Status": "Active"}
    ]
    
    # Scenario 1: New file with custom name
    print("\n📄 Scenario 1: Creating new file with custom name")
    
    custom_file_name = f"UserReport_Result_{current_date}.json"
    
    context1 = ExecutionContext(
        workflow_id="test-workflow",
        instance_id="test-instance-001",
        step_id="drive-write-1",
        input_data={
            "file_name": custom_file_name,
            "folder_id": "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182",
            "file_type": "json",
            "content_source": "input_data",
            "content_data": test_data
        },
        previous_outputs={},
        global_variables={}
    )
    
    result1 = await drive_component.execute(context1)
    
    print(f"Custom file creation: {result1.success}")
    if result1.success:
        print(f"File: {custom_file_name}")
        print(f"Details: {result1.output_data}")
    
    # Scenario 2: Standard naming pattern
    print("\n📄 Scenario 2: Standard Result file naming")
    
    standard_file_name = f"Result_{current_date}.csv"
    
    context2 = ExecutionContext(
        workflow_id="test-workflow",
        instance_id="test-instance-001",
        step_id="drive-write-2", 
        input_data={
            "file_name": standard_file_name,
            "folder_id": "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182",
            "file_type": "csv",
            "content_source": "input_data",
            "content_data": test_data
        },
        previous_outputs={},
        global_variables={}
    )
    
    result2 = await drive_component.execute(context2)
    
    print(f"Standard file creation: {result2.success}")
    if result2.success:
        print(f"File: {standard_file_name}")
        print(f"Details: {result2.output_data}")

async def main():
    """Main test function"""
    
    try:
        # Test 1: Read from sheets and upload to drive
        await test_sheets_to_drive_workflow()
        
        # Test 2: File naming logic
        await test_file_name_logic()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
