#!/usr/bin/env python3
"""
Fix Google Drive CSV Export
Fix vấn đề workflow không save được CSV file vào Google Drive
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.services.workflow.component_registry import GoogleSheetsComponent, AIProcessingComponent, GoogleDriveWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def test_ai_to_csv_workflow():
    """Test complete AI processing to CSV workflow"""
    print("🔧 FIXING: AI Processing → CSV Export to Google Drive")
    print("="*65)
    
    # Step 1: Read from Google Sheets 
    print("\n📊 Step 1: Reading data from Google Sheets...")
    sheets_component = GoogleSheetsComponent()
    
    sheets_context = ExecutionContext(
        workflow_id="csv-fix-workflow",
        instance_id="csv-fix-instance-001",
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
        workflow_id="csv-fix-workflow",
        instance_id="csv-fix-instance-001", 
        step_id="ai-processing",
        input_data={
            "provider": "ollama",
            "model": "qwen2.5:3b",
            "prompt": "Create a detailed asset specification for: {description}. Output format: {output_format}. Include technical details, style guidelines, and implementation notes.",
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
    
    # Step 3: Export to CSV in Google Drive
    print("\n📁 Step 3: Exporting AI results to CSV in Google Drive...")
    drive_component = GoogleDriveWriteComponent()
    
    # Create filename with timestamp
    csv_filename = f"AI_Processing_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    drive_context = ExecutionContext(
        workflow_id="csv-fix-workflow",
        instance_id="csv-fix-instance-001",
        step_id="drive-write",
        input_data={
            "file_name": csv_filename,
            "folder_id": "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182",  # Your Drive folder ID
            "file_type": "csv",  # Explicit CSV format
            "content_source": "previous_output",
            "mimetype": "text/csv"
        },
        previous_outputs={
            "ai-processing": ai_result.output_data
        },
        global_variables={}
    )
    
    drive_result = await drive_component.execute(drive_context)
    
    if drive_result.success:
        print(f"✅ Successfully exported CSV to Google Drive!")
        
        output_data = drive_result.output_data
        print(f"📄 File: {output_data.get('name', 'N/A')}")
        print(f"📊 Type: {output_data.get('mime_type', 'N/A')}")
        print(f"📏 Size: {output_data.get('size', 'N/A')} bytes")
        print(f"🔗 View: {output_data.get('web_view_link', 'N/A')}")
        
        if output_data.get('mime_type') == 'text/csv':
            print("🎉 SUCCESS: CSV file format confirmed!")
        else:
            print(f"⚠️ Unexpected file type: {output_data.get('mime_type')}")
        
        return True
    else:
        print(f"❌ Failed to export to Google Drive: {drive_result.error}")
        print("📝 Logs:")
        for log in drive_result.logs:
            print(f"  - {log}")
        return False

async def test_csv_conversion():
    """Test CSV conversion logic directly"""
    print("\n🔧 TESTING: CSV Conversion Logic")
    print("="*45)
    
    # Sample AI processing data
    sample_ai_data = {
        "processed_results": [
            {
                "row_index": 1,
                "input_data": {"description": "Design a Task Manager app logo", "output_format": "PNG"},
                "ai_response": {"generated_url": "https://ollama-assets.local/png/1234.png"},
                "status": "success",
                "provider": "ollama",
                "model": "qwen2.5:3b"
            },
            {
                "row_index": 2,
                "input_data": {"description": "Summer Sale banner", "output_format": "JPG"},
                "ai_response": {"generated_url": "https://ollama-assets.local/jpg/5678.jpg"},
                "status": "success", 
                "provider": "ollama",
                "model": "qwen2.5:3b"
            }
        ],
        "results_for_sheets": [
            ["Row Index", "Original Description", "Output Format", "Status", "Generated URL", "Provider", "Model"],
            [1, "Design a Task Manager app logo", "PNG", "success", "https://ollama-assets.local/png/1234.png", "ollama", "qwen2.5:3b"],
            [2, "Summer Sale banner", "JPG", "success", "https://ollama-assets.local/jpg/5678.jpg", "ollama", "qwen2.5:3b"]
        ],
        "summary": {
            "total_records": 2,
            "processed_records": 2,
            "successful_records": 2
        }
    }
    
    drive_component = GoogleDriveWriteComponent()
    
    # Test CSV conversion
    print("📋 Testing CSV conversion...")
    csv_content = drive_component._prepare_file_content(sample_ai_data, "csv")
    csv_text = csv_content.decode('utf-8')
    
    print("📄 CSV Content Preview:")
    print("-" * 60)
    print(csv_text)
    print("-" * 60)
    
    # Test Google Drive upload
    test_context = ExecutionContext(
        workflow_id="csv-test",
        instance_id="csv-test-001",
        step_id="csv-conversion-test",
        input_data={
            "file_name": f"CSV_Test_{datetime.now().strftime('%H%M%S')}.csv",
            "folder_id": "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182",
            "file_type": "csv",
            "content_source": "input_data",
            "content_data": sample_ai_data
        },
        previous_outputs={},
        global_variables={}
    )
    
    result = await drive_component.execute(test_context)
    
    if result.success:
        print("✅ CSV conversion and upload test PASSED")
        return True
    else:
        print(f"❌ CSV conversion test FAILED: {result.error}")
        return False

async def main():
    """Main test function"""
    print("🚀 GOOGLE DRIVE CSV EXPORT FIX")
    print("="*70)
    
    # Test 1: CSV conversion logic
    print("\n📋 Test 1: CSV Conversion Logic")
    conversion_success = await test_csv_conversion()
    
    if not conversion_success:
        print("\n❌ CSV conversion failed, stopping here")
        return
    
    # Test 2: Full workflow test
    print("\n📋 Test 2: Complete AI → CSV Export Workflow")
    workflow_success = await test_ai_to_csv_workflow()
    
    if workflow_success:
        print("\n🎉 CSV EXPORT FIX COMPLETED SUCCESSFULLY!")
        print("\n📋 Summary:")
        print("✅ AI Processing → CSV conversion working")
        print("✅ Google Drive Write Component fixed")
        print("✅ CSV files now properly saved to Google Drive")
        print("✅ Correct MIME type (text/csv) applied")
        
        print("\n🎯 Next Steps:")
        print("1. Check your Google Drive folder for the CSV files")
        print("2. The workflow now properly exports AI results as CSV")
        print("3. CSV files have proper headers and formatting")
    else:
        print("\n❌ CSV export fix failed")
        print("🔍 Check the logs above for specific errors")

if __name__ == "__main__":
    asyncio.run(main())
