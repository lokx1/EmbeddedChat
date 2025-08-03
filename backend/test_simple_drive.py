#!/usr/bin/env python3
"""
Simple Google Drive Write test with sample data
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.workflow.component_registry import GoogleDriveWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def test_simple_drive_upload():
    """Test Google Drive upload with sample data"""
    
    print("=== Simple Google Drive Upload Test ===")
    
    # Sample data from a typical Google Sheets workflow result
    sample_data = [
        {"Name": "John Doe", "Age": "30", "City": "New York", "Status": "Active"},
        {"Name": "Jane Smith", "Age": "25", "City": "San Francisco", "Status": "Pending"},
        {"Name": "Bob Johnson", "Age": "35", "City": "Chicago", "Status": "Active"},
        {"Name": "Alice Brown", "Age": "28", "City": "Los Angeles", "Status": "Active"}
    ]
    
    drive_component = GoogleDriveWriteComponent()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Basic JSON upload",
            "file_name": "user_data.json",
            "file_type": "json",
            "data": sample_data
        },
        {
            "name": "CSV format with smart naming",
            "file_name": "users.csv", 
            "file_type": "csv",
            "data": sample_data
        },
        {
            "name": "Text summary",
            "file_name": "summary.txt",
            "file_type": "text",
            "data": f"Data Summary:\nTotal records: {len(sample_data)}\nGenerated: {datetime.now()}"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📁 Test {i}: {scenario['name']}")
        
        context = ExecutionContext(
            workflow_id="test-workflow",
            instance_id="test-instance-001",
            step_id=f"drive-write-{i}",
            input_data={
                "file_name": scenario["file_name"],
                "folder_id": "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182",  # Your folder
                "file_type": scenario["file_type"],
                "content_source": "previous_output",
                "mimetype": ""
            },
            previous_outputs={
                "data_source": {
                    "data": scenario["data"]
                }
            },
            global_variables={}
        )
        
        result = await drive_component.execute(context)
        
        print(f"✅ Success: {result.success}")
        if result.success:
            file_info = result.output_data.get('file_info', {})
            print(f"📄 Final filename: {file_info.get('filename', 'unknown')}")
            print(f"📂 Folder: {file_info.get('folder_id', 'unknown')}")
            print(f"📊 File size: {file_info.get('size', 0)} bytes")
            print(f"⏱️ Status: {result.output_data.get('status', 'unknown')}")
        else:
            print(f"❌ Error: {result.error}")
        
        print(f"⏱️ Execution time: {result.execution_time_ms}ms")
        
        # Show key logs
        important_logs = [log for log in result.logs if any(keyword in log.lower() 
                         for keyword in ['final', 'filename', 'upload', 'success', 'error'])]
        if important_logs:
            print("📝 Key logs:")
            for log in important_logs[:3]:  # Show first 3 important logs
                print(f"   - {log}")
        
        print("-" * 60)

async def test_file_naming_scenarios():
    """Test different file naming scenarios"""
    
    print("\n=== File Naming Test ===")
    
    drive_component = GoogleDriveWriteComponent()
    
    naming_tests = [
        {
            "input": "data.json",
            "description": "Simple filename"
        },
        {
            "input": "Result_existing.csv",
            "description": "Already has Result_ prefix"  
        },
        {
            "input": "MyReport.xlsx",
            "description": "Custom report name"
        },
        {
            "input": "output",
            "description": "No extension"
        }
    ]
    
    for test in naming_tests:
        print(f"\n🏷️ Testing: {test['description']}")
        print(f"Input: '{test['input']}'")
        
        # Test the smart filename generation
        smart_name = await drive_component._generate_smart_filename(
            test["input"], 
            "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182"
        )
        
        print(f"Output: '{smart_name}'")
        print(f"✅ Result follows pattern: {'Result_' in smart_name}")

if __name__ == "__main__":
    asyncio.run(test_simple_drive_upload())
    asyncio.run(test_file_naming_scenarios())
