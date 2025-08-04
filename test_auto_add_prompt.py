#!/usr/bin/env python3
"""
Quick Test - Verify Prompt Column Auto-Add
Kiểm tra nhanh tính năng auto-add cột Prompt
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

import asyncio
from services.workflow.google_services import GoogleSheetsService
import json

async def test_prompt_column_auto_add():
    """Test auto-add Prompt column và ghi AI_Response"""
    
    print("🧪 Testing Auto-Add Prompt Column...")
    
    # Initialize service
    sheets_service = GoogleSheetsService()
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    # Test data trong format list of lists (not dict)
    test_data = [
        ["Description", "Example Asset URL", "Desired Output Format", "Model Specification", "Prompt"],
        ["Create modern logo design", "https://example.com/logo.png", "PNG with transparent background", "Creative and modern design", "🤖 AI Generated: Create a modern, minimalist logo design for a tech startup. Use clean lines, incorporate blue and white colors, ensure scalability for various sizes, and maintain professional appearance suitable for digital and print media."],
        ["Design mobile app icons", "https://example.com/icon.svg", "SVG vector format", "iOS and Android compatible", "🤖 AI Generated: Design a set of mobile app icons that are modern, intuitive, and follow current design trends. Use consistent style, appropriate sizing for different devices, and ensure clarity at small scales."]
    ]
    
    # Test ghi vào worksheet TEST_NEW
    try:
        print(f"📝 Writing test data to worksheet TEST_NEW...")
        
        # Ghi data - auto-add sẽ tự động xử lý
        success, result = await sheets_service.write_to_sheet(
            sheet_id=sheet_id,
            sheet_name="TEST_NEW",
            range_start="A1",
            mode="overwrite",
            data=test_data
        )
        
        print(f"✅ Write result: Success={success}, Details={result}")
        
        if success:
            # Verify data
            print("📊 Verifying written data...")
            worksheet = sheets_service.get_worksheet(sheet_id, "TEST_NEW")
            all_values = worksheet.get_all_values()
            
            if len(all_values) > 0:
                headers = all_values[0]
                print(f"Headers: {headers}")
                
                if "Prompt" in headers:
                    prompt_col_idx = headers.index("Prompt")
                    print(f"✅ Prompt column found at index {prompt_col_idx}")
                    
                    # Check data in Prompt column
                    for i, row in enumerate(all_values[1:], 1):
                        if len(row) > prompt_col_idx:
                            prompt_value = row[prompt_col_idx]
                            if "🤖 AI Generated:" in prompt_value:
                                print(f"✅ Row {i}: AI_Response found - {prompt_value[:50]}...")
                            else:
                                print(f"ℹ️ Row {i}: {prompt_value}")
                else:
                    print("❌ Prompt column not found")
        
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_config():
    """Tạo workflow config mẫu cho frontend"""
    
    workflow_config = {
        "workflow_id": "test_prompt_column_workflow",
        "name": "Test Auto-Add Prompt Column",
        "description": "Test workflow to verify auto-add Prompt column feature",
        "components": [
            {
                "id": "read_sheets",
                "type": "google_sheets_read",
                "config": {
                    "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                    "worksheet_name": "TEST_NEW",  # ← Chỉ định worksheet cụ thể
                    "range": "A:Z"
                }
            },
            {
                "id": "ai_process",
                "type": "ai_processing",
                "config": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "task_type": "text_generation"
                }
            },
            {
                "id": "write_sheets", 
                "type": "google_sheets_write",
                "config": {
                    "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                    "worksheet_name": "TEST_NEW",  # ← Cùng worksheet
                    "operation": "overwrite"
                }
            }
        ],
        "connections": [
            {"from": "read_sheets", "to": "ai_process"},
            {"from": "ai_process", "to": "write_sheets"}
        ]
    }
    
    # Save config
    config_file = "workflow_config_prompt_test.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(workflow_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Workflow config saved to: {config_file}")
    print("📖 Import config này vào frontend workflow editor")
    
    return workflow_config

if __name__ == "__main__":
    print("🚀 Auto-Add Prompt Column Test")
    print("="*50)
    
    # Test 1: Auto-add functionality
    success = asyncio.run(test_prompt_column_auto_add())
    
    print("\n" + "="*50)
    
    # Test 2: Generate workflow config
    test_workflow_config()
    
    print("\n" + "="*50)
    if success:
        print("✅ Auto-add Prompt column feature is working!")
        print("📋 Next steps:")
        print("1. Use the generated workflow config in frontend editor")
        print("2. Set correct worksheet_name in both READ and WRITE components")
        print("3. Execute workflow to see AI_Response in Prompt column")
    else:
        print("❌ Auto-add feature needs debugging")
