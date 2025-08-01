#!/usr/bin/env python3
"""
Simplified test for Google Sheets Write configuration
"""

import requests
import json
from datetime import datetime

def test_google_sheets_write_simple():
    """Test Google Sheets Write component configuration"""
    base_url = "http://localhost:8000/api/v1"
    
    # Your Google Sheets URL
    sheet_url = "https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit?gid=0#gid=0"
    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    
    print(f"📊 Testing Google Sheets Write for Sheet ID: {sheet_id}")
    print(f"🎯 Target: Sheet2 (next tab)")
    
    # Workflow data với Google Sheets Write component
    workflow_data = {
        "nodes": [
            {
                "id": "trigger-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Manual Trigger",
                    "type": "manual_trigger",
                    "config": {}
                }
            },
            {
                "id": "sheets-write-1",
                "type": "google_sheets_write",
                "position": {"x": 400, "y": 100},
                "data": {
                    "label": "Write to Sheet2",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": sheet_id,
                        "sheet_name": "Sheet2",  # Trang tính kế bên
                        "range": "A1",
                        "mode": "append",
                        "data_format": "auto"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "trigger-1",
                "target": "sheets-write-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # Sample data để ghi
    sample_data = [
        ["Timestamp", "Task", "Status", "Notes"],
        [str(datetime.now()), "User Registration", "Success", "New user registered via workflow"],
        [str(datetime.now()), "Data Processing", "In Progress", "Processing user data"],
        [str(datetime.now()), "Email Notification", "Pending", "Sending welcome email"]
    ]
    
    # Tạo instance trực tiếp
    instance_payload = {
        "name": f"Google Sheets Write Test - {datetime.now().strftime('%H:%M:%S')}",
        "workflow_data": workflow_data,
        "input_data": {
            "data": sample_data
        },
        "created_by": "test_user"
    }
    
    print("\n🚀 Creating workflow instance...")
    instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
    print(f"Instance response: {instance_response.status_code}")
    
    if instance_response.status_code != 200:
        print(f"❌ Failed to create instance: {instance_response.text}")
        return False
    
    instance_data = instance_response.json()
    instance_id = instance_data["instance_id"]
    print(f"✅ Instance created with ID: {instance_id}")
    
    # Execute workflow instance
    print("\n🚀 Executing workflow...")
    execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute", json={
        "input_data": sample_data
    })
    print(f"Execute response: {execute_response.status_code}")
    
    if execute_response.status_code != 200:
        print(f"❌ Failed to execute: {execute_response.text}")
        return False
    
    print("✅ Workflow execution started")
    
    # Check status
    import time
    time.sleep(3)
    
    status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
    if status_response.status_code == 200:
        status_data = status_response.json()
        instance = status_data["data"]["instance"]  # Fix: add ["instance"] level
        
        print(f"\n📋 Final Status: {instance['status']}")
        
        if instance.get('output_data'):
            output = instance['output_data']
            print("📤 Output Data:")
            print(json.dumps(output, indent=2))
            
            # Check if Google Sheets Write component was executed
            if 'node_outputs' in output and 'sheets-write-1' in output['node_outputs']:
                sheets_output = output['node_outputs']['sheets-write-1']
                print(f"\n✅ Google Sheets Write Result:")
                print(f"   - Operation: {sheets_output.get('operation', 'N/A')}")
                print(f"   - Target Sheet: {sheets_output.get('sheet_info', {}).get('sheet_name', 'N/A')}")
                print(f"   - Rows Written: {sheets_output.get('data_written', {}).get('rows_count', 'N/A')}")
                
                # Show the component config that was used
                node_config = None
                for node in instance['workflow_data']['nodes']:
                    if node['id'] == 'sheets-write-1':
                        node_config = node['data']['config']
                        break
                
                if node_config:
                    print(f"\n⚙️ Configuration Used:")
                    print(f"   - Sheet ID: {node_config['sheet_id']}")
                    print(f"   - Sheet Name: {node_config['sheet_name']}")
                    print(f"   - Range: {node_config['range']}")
                    print(f"   - Mode: {node_config['mode']}")
                    print(f"   - Data Format: {node_config['data_format']}")
        
        if instance.get('error_message'):
            print(f"❌ Error: {instance['error_message']}")
        
        # Show execution timing
        if instance.get('started_at') and instance.get('completed_at'):
            print(f"\n⏱️ Execution Time:")
            print(f"   - Started: {instance['started_at']}")
            print(f"   - Completed: {instance['completed_at']}")
        
        # Show URLs
        original_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid=0#gid=0"
        sheet2_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=1"
        
        print(f"\n🔗 Original Sheet: {original_url}")
        print(f"🔗 Target Sheet2: {sheet2_url}")
        
        return True
    else:
        print(f"❌ Failed to get status: {status_response.text}")
        return False

def show_config_options():
    """Show different configuration options for Google Sheets Write"""
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    print("\n🔧 Google Sheets Write Configuration Options:")
    
    configs = [
        {
            "name": "Sheet2 (Next Tab)",
            "sheet_name": "Sheet2",
            "mode": "append",
            "description": "Ghi vào trang tính kế bên"
        },
        {
            "name": "Results Tab", 
            "sheet_name": "Results",
            "mode": "overwrite", 
            "description": "Ghi kết quả và ghi đè dữ liệu cũ"
        },
        {
            "name": "New Data Tab",
            "sheet_name": "Data_" + datetime.now().strftime("%Y%m%d"),
            "mode": "clear_write",
            "description": "Tạo trang với tên theo ngày"
        }
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n{i}. {config['name']}:")
        print(f"   📝 Sheet Name: {config['sheet_name']}")
        print(f"   📝 Mode: {config['mode']}")
        print(f"   📝 Description: {config['description']}")
        print(f"   🔗 URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid={i}")

if __name__ == "__main__":
    print("=== Google Sheets Write to Next Tab Test ===")
    
    # Show configuration options
    show_config_options()
    
    # Run test
    print("\n" + "="*50)
    success = test_google_sheets_write_simple()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("\n💡 Bạn có thể:")
        print("   1. Thay đổi 'sheet_name' để ghi vào trang khác")
        print("   2. Sử dụng 'mode': 'append', 'overwrite', hoặc 'clear_write'")
        print("   3. Thay đổi 'range' để ghi vào vị trí khác (VD: 'B5')")
    else:
        print("\n❌ Test failed")
    
    print(f"\n📌 Note: Hiện tại đây là simulation.")
    print("📌 Để ghi thực tế vào Google Sheets cần API credentials.")
