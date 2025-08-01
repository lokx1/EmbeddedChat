#!/usr/bin/env python3
"""
Test Google Sheets Write component with configuration
"""

import requests
import json
from datetime import datetime

def test_google_sheets_write_workflow():
    """Test creating and executing a workflow with Google Sheets Write component"""
    base_url = "http://localhost:8000/api/v1"
    
    # 1. Create a workflow template with Google Sheets Write component
    workflow_data = {
        "nodes": [
            {
                "id": "trigger-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Manual Trigger",
                    "type": "manual_trigger",
                    "config": {
                        "trigger_data": {"test": "data", "timestamp": str(datetime.now())}
                    }
                }
            },
            {
                "id": "sheets-write-1",
                "type": "google_sheets_write",
                "position": {"x": 400, "y": 100},
                "data": {
                    "label": "Google Sheets Write",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",  # Test sheet
                        "sheet_name": "Class Data",
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
    
    # Save workflow template
    save_payload = {
        "name": "Google Sheets Write Test",
        "description": "Test workflow with Google Sheets Write component",
        "workflow_data": workflow_data,
        "category": "test"
    }
    
    print("🚀 Creating workflow template...")
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    print(f"Save response: {save_response.status_code}")
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        print(f"Template response: {json.dumps(template_data, indent=2)}")
        template_id = template_data["id"]  # Fix: remove ["data"] level
        print(f"✅ Template created with ID: {template_id}")
        
        # 2. Execute the workflow
        print("\n📊 Executing workflow...")
        execute_payload = {
            "template_id": template_id,
            "name": f"Test execution {datetime.now().strftime('%H:%M:%S')}",
            "input_data": {
                "test_data": [
                    ["Name", "Age", "City"],
                    ["John Doe", "30", "New York"],
                    ["Jane Smith", "25", "San Francisco"]
                ]
            }
        }
        
        execute_response = requests.post(f"{base_url}/workflow/execute", json=execute_payload)
        print(f"Execute response: {execute_response.status_code}")
        
        if execute_response.status_code == 200:
            execution_data = execute_response.json()
            instance_id = execution_data["data"]["id"]
            print(f"✅ Workflow execution started with ID: {instance_id}")
            
            # 3. Check execution status
            import time
            time.sleep(2)
            
            status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                instance = status_data["data"]
                print(f"\n📋 Execution Status: {instance['status']}")
                
                if instance.get('output_data'):
                    print("📤 Output Data:")
                    print(json.dumps(instance['output_data'], indent=2))
                
                if instance.get('error_message'):
                    print(f"❌ Error: {instance['error_message']}")
                    
                if instance.get('execution_logs'):
                    print("📝 Execution Logs:")
                    for log in instance['execution_logs']:
                        print(f"  - {log}")
                        
                return True
        else:
            print(f"❌ Failed to execute workflow: {execute_response.text}")
            return False
    else:
        print(f"❌ Failed to create template: {save_response.text}")
        return False

def test_component_config():
    """Test that components can receive configuration from frontend"""
    print("\n🔧 Testing component configuration...")
    
    # Get available components
    components_response = requests.get("http://localhost:8000/api/v1/workflow/components")
    if components_response.status_code == 200:
        components = components_response.json()["data"]
        
        # Find Google Sheets Write component
        write_component = None
        for comp in components:
            if comp["type"] == "google_sheets_write":
                write_component = comp
                break
        
        if write_component:
            print("✅ Found Google Sheets Write component")
            print(f"Parameters: {len(write_component['parameters'])}")
            for param in write_component['parameters']:
                print(f"  - {param['name']}: {param['type']} ({'required' if param['required'] else 'optional'})")
            return True
        else:
            print("❌ Google Sheets Write component not found")
            return False
    else:
        print(f"❌ Failed to get components: {components_response.text}")
        return False

if __name__ == "__main__":
    print("=== Google Sheets Write Component Test ===\n")
    
    # Test 1: Component configuration
    config_success = test_component_config()
    
    # Test 2: Workflow execution with configuration
    if config_success:
        workflow_success = test_google_sheets_write_workflow()
        
        if workflow_success:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Workflow test failed")
    else:
        print("\n❌ Configuration test failed")
