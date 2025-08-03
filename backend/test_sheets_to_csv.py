#!/usr/bin/env python3
"""
Test Google Sheets to CSV conversion in Google Drive Write component
"""
import json
import asyncio
from src.services.workflow.component_registry import GoogleDriveWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def test_sheets_to_csv():
    print("=== Google Sheets to CSV Conversion Test ===")
    
    # Sample Google Sheets data (similar to your screenshot)
    sheets_data = {
        "values": [
            ["Description", "Example Asset URL", "Desired Output Format", "Model Specification"],
            ["Design a Task Manager app logo", "https://static.wikia.nocookie.net/logopaedia/images/9/97/Task_Manager_2024.png", "PNG", "OpenAI"],
            ["Summer Sale banner for a fashion store", "https://images.vexels.com/content/107842/preview/summer-sale-poster-design-illustration-836lb3.png", "JPG", "Claude"],
            ["MP3 audio notification", "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRj5MjCGTOIXy7d-IzumzGSlqDXFPAHDA&s", "MP3 audio", "Claude"],
            ["Video thumbnail", "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQj4IMrFsaMJgODN9UKOsNVZiRulk3mnCQ&s", "PNG", "OpenAI"]
        ],
        "records": [
            {
                "Description": "Design a Task Manager app logo",
                "Example Asset URL": "https://static.wikia.nocookie.net/logopaedia/images/9/97/Task_Manager_2024.png",
                "Desired Output Format": "PNG",
                "Model Specification": "OpenAI"
            },
            {
                "Description": "Summer Sale banner for a fashion store", 
                "Example Asset URL": "https://images.vexels.com/content/107842/preview/summer-sale-poster-design-illustration-836lb3.png",
                "Desired Output Format": "JPG",
                "Model Specification": "Claude"
            },
            {
                "Description": "MP3 audio notification",
                "Example Asset URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRj5MjCGTOIXy7d-IzumzGSlqDXFPAHDA&s",
                "Desired Output Format": "MP3 audio", 
                "Model Specification": "Claude"
            },
            {
                "Description": "Video thumbnail",
                "Example Asset URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQj4IMrFsaMJgODN9UKOsNVZiRulk3mnCQ&s",
                "Desired Output Format": "PNG",
                "Model Specification": "OpenAI"
            }
        ],
        "spreadsheet_info": {
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": "Sheet1", 
            "total_rows": 5,
            "total_columns": 4,
            "columns": ["Description", "Example Asset URL", "Desired Output Format", "Model Specification"]
        }
    }
    
    component = GoogleDriveWriteComponent()
    
    # Test 1: Auto-detect file type (should convert to CSV)
    print("\n📋 Test 1: Auto-detect file type with Google Sheets data")
    context = ExecutionContext(
        workflow_id="test-workflow",
        instance_id="test-instance", 
        step_id="test-step",
        node_id="drive-write-1",
        input_data={
            "file_name": "TaskManagement_Data.csv",
            "file_type": "auto",  # Auto-detect 
            "folder_id": "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182",
            "content_source": "previous_output"
        },
        previous_outputs={
            "sheets-read-1": sheets_data
        },
        global_variables={}
    )
    
    result = await component.execute(context)
    print(f"✅ Result: {result.success}")
    print(f"📄 File extension detected: {result.logs}")
    
    # Test 2: Explicit CSV format
    print("\n📋 Test 2: Explicit CSV format")
    context.input_data["file_type"] = "csv"
    context.input_data["file_name"] = "TaskManagement_Explicit.csv"
    
    result = await component.execute(context)
    print(f"✅ Result: {result.success}")
    print(f"📄 Output data: {json.dumps(result.output_data, indent=2)}")
    
    # Test 3: Check CSV content format
    print("\n📋 Test 3: Preview CSV content")
    csv_content = component._prepare_file_content(sheets_data, "csv")
    csv_text = csv_content.decode('utf-8')
    print("CSV Content Preview:")
    print("-" * 50)
    print(csv_text[:500] + "..." if len(csv_text) > 500 else csv_text)
    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_sheets_to_csv())
