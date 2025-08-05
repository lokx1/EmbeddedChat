"""
Debug script để kiểm tra workflow config từ frontend có chứa đúng mode và data_format không
"""
import json
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from src.services.workflow.component_registry import GoogleSheetsWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def debug_frontend_config():
    """Giả lập workflow data từ frontend với config đầy đủ"""
    
    # Giả lập node data từ frontend - chứa config mode và data_format
    frontend_node_data = {
        "id": "sheets_write_1",
        "type": "google_sheets_write",
        "data": {
            "label": "Google Sheets Write",
            "type": "google_sheets_write",
            "config": {
                "sheet_id": "1Z2X3Y4W5V6U7T8S9R0Q1P2O3N4M5L6K7J8I9H0G",
                "sheet_name": "HEYDO",
                "range": "A1",
                "mode": "overwrite",  # ĐÂY LÀ QUAN TRỌNG
                "data_format": "auto"  # ĐÂY CŨNG QUAN TRỌNG
            }
        }
    }
    
    print("=== Frontend Node Config ===")
    print(json.dumps(frontend_node_data["data"]["config"], indent=2))
    
    # Giả lập execution context với đầy đủ required fields
    context = ExecutionContext(
        workflow_id="test_workflow",
        instance_id="test_instance",
        step_id="sheets_write_1",
        input_data={
            "results_for_sheets": [
                {
                    "id": "1",
                    "original": "Create a social media post",
                    "ai_generated": "🚀 Exciting news! Our new product launch is just around the corner. Stay tuned for amazing features that will revolutionize your workflow! #Innovation #ProductLaunch #TechNews"
                }
            ]
        },
        previous_outputs={},
        global_variables={"step_config": frontend_node_data["data"]["config"]}  # Config từ frontend
    )
    
    print("\n=== Step Config from Frontend ===")
    print(json.dumps(context.global_variables.get("step_config", {}), indent=2))
    
    # Test thực thi component với config này
    component = GoogleSheetsWriteComponent()
    
    print("\n=== Testing Component Execution ===")
    try:
        result = await component.execute(context)
        print(f"✅ Execution successful: {result.success}")
        print(f"Data: {result.data}")
        if result.error:
            print(f"❌ Error: {result.error}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Kiểm tra metadata có đúng không
    print("\n=== Component Metadata ===")
    metadata = component.get_metadata()
    mode_param = next((p for p in metadata.parameters if p.name == "mode"), None)
    data_format_param = next((p for p in metadata.parameters if p.name == "data_format"), None)
    
    if mode_param:
        print(f"✅ Mode parameter found:")
        print(f"  - Default: {mode_param.default_value}")
        print(f"  - Options: {[opt.get('value') for opt in mode_param.options or []]}")
    
    if data_format_param:
        print(f"✅ Data format parameter found:")
        print(f"  - Default: {data_format_param.default_value}")
        print(f"  - Options: {[opt.get('value') for opt in data_format_param.options or []]}")

if __name__ == "__main__":
    asyncio.run(debug_frontend_config())
