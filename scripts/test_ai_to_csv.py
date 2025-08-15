#!/usr/bin/env python3
"""
Test AI Processing to CSV conversion
"""
import json
import asyncio
from src.services.workflow.component_registry import GoogleDriveWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def test_ai_processing_to_csv():
    print("=== AI Processing to CSV Conversion Test ===")
    
    # Sample AI processing data (from the logs)
    ai_data = {
        "processed_results": [
            {
                "row_index": 1,
                "input_data": {"Description": "Design a Task Manager app logo"},
                "ai_response": {"type": "ollama_asset_generation", "generated_url": "https://example.com/1.png"},
                "status": "success"
            }
        ],
        "results_for_sheets": [
            ["Row Index", "Original Description", "Output Format", "Status", "Generated URL", "Provider", "Model"],
            [1, "Design a Task Manager app logo", "PNG", "success", "https://ollama-assets.local/png/0.png", "ollama", "qwen3:8b"],
            [2, "Summer Sale banner", "JPG", "success", "https://demo-assets.example.com/png/6334.png", "ollama", "qwen3:8b"],
            [3, "MP3 audio notification", "MP3", "success", "https://demo-assets.example.com/png/6334.png", "ollama", "qwen3:8b"],
            [4, "Video thumbnail", "PNG", "success", "https://demo-assets.example.com/png/6334.png", "ollama", "qwen3:8b"]
        ],
        "summary": {
            "total_records": 4,
            "processed_records": 4,
            "successful_records": 4
        }
    }
    
    component = GoogleDriveWriteComponent()
    
    # Test AI processing data conversion
    print("\n📋 Test: AI Processing data to CSV")
    context = ExecutionContext(
        workflow_id="test-workflow",
        instance_id="test-instance", 
        step_id="test-step",
        node_id="drive-write-1",
        input_data={
            "file_name": "AI_Results.csv",
            "file_type": "auto",  # Auto-detect 
            "folder_id": "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182",
            "content_source": "previous_output"
        },
        previous_outputs={
            "ai-processing-1": ai_data
        },
        global_variables={}
    )
    
    result = await component.execute(context)
    print(f"✅ Result: {result.success}")
    
    if result.success:
        output_data = result.output_data
        print(f"📄 File: {output_data.get('name', 'N/A')}")
        print(f"📊 MIME: {output_data.get('mime_type', 'N/A')}")
        print(f"📏 Size: {output_data.get('size', 'N/A')} bytes")
        
        if output_data.get('mime_type') == 'text/csv':
            print("🎉 SUCCESS: AI data converted to CSV!")
        else:
            print(f"⚠️ Unexpected MIME type: {output_data.get('mime_type')}")
            
        # Show logs
        print("\n📝 Conversion Logs:")
        for log in result.logs[:5]:
            print(f"  - {log}")
    else:
        print(f"❌ Error: {result.error}")
        print("📝 Error Logs:")
        for log in result.logs:
            print(f"  - {log}")
    
    # Test CSV content preview
    print("\n📋 CSV Content Preview:")
    csv_content = component._prepare_file_content(ai_data, "csv")
    csv_text = csv_content.decode('utf-8')
    print("-" * 60)
    print(csv_text[:500] + "..." if len(csv_text) > 500 else csv_text)
    print("-" * 60)

if __name__ == "__main__":
    asyncio.run(test_ai_processing_to_csv())
