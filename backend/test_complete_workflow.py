#!/usr/bin/env python3
"""
Test complete workflow: Google Sheets Read -> Google Drive Write
"""
import requests
import json
from datetime import datetime

def test_sheets_to_drive_workflow():
    """Test creating workflow that reads from sheets and writes to drive"""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Create a complete workflow: Trigger -> Sheets Read -> Drive Write
    workflow_data = {
        "nodes": [
            {
                "id": "trigger-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "config": {}
                }
            },
            {
                "id": "sheets-read-1", 
                "type": "google_sheets",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "Read Google Sheets",
                    "type": "google_sheets",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "Sheet1", 
                        "range": "A:Z",
                        "output_format": "records"
                    }
                }
            },
            {
                "id": "drive-write-1",
                "type": "google_drive_write", 
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "Save to Google Drive",
                    "type": "google_drive_write",
                    "config": {
                        "file_name": "WorkflowResult.json",
                        "folder_id": "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182",
                        "file_type": "json",
                        "content_source": "previous_output",
                        "mimetype": ""
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "trigger-1",
                "target": "sheets-read-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            },
            {
                "id": "edge-2", 
                "source": "sheets-read-1",
                "target": "drive-write-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # 1. Save workflow template
    save_payload = {
        "name": "Sheets to Drive Workflow",
        "description": "Read data from Google Sheets and save to Google Drive", 
        "workflow_data": workflow_data,
        "category": "integration"
    }
    
    print("🚀 Creating Sheets to Drive workflow...")
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    print(f"Template save status: {save_response.status_code}")
    
    if save_response.status_code != 200:
        print(f"❌ Failed to save template: {save_response.text}")
        return False
    
    template_data = save_response.json()
    template_id = template_data["data"]["workflow_id"]
    print(f"✅ Template created: {template_id}")
    
    # 2. Create instance
    instance_payload = {
        "template_id": template_id,
        "name": f"Sheets to Drive - {datetime.now().strftime('%H:%M:%S')}",
        "workflow_data": workflow_data,
        "input_data": {}
    }
    
    print("\n📊 Creating workflow instance...")
    instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
    
    if instance_response.status_code != 200:
        print(f"❌ Failed to create instance: {instance_response.text}")
        return False
    
    instance_data = instance_response.json()
    instance_id = instance_data["instance_id"]
    print(f"✅ Instance created: {instance_id}")
    
    # 3. Execute workflow
    print("\n🚀 Executing workflow...")
    execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
    
    if execute_response.status_code != 200:
        print(f"❌ Failed to execute: {execute_response.text}")
        return False
    
    print("✅ Workflow execution started")
    
    # 4. Check results
    import time
    time.sleep(3)  # Wait for execution
    
    status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
    if status_response.status_code == 200:
        status_data = status_response.json()
        instance = status_data["data"]["instance"]
        
        print(f"\n📋 Final Status: {instance['status']}")
        
        if instance.get('output_data'):
            print("📤 Final Output:")
            print(json.dumps(instance['output_data'], indent=2))
        
        if instance.get('error_message'):
            print(f"❌ Error: {instance['error_message']}")
        
        # Show step details
        steps = instance.get('steps', [])
        if steps:
            print(f"\n📊 Execution Steps ({len(steps)}):")
            for i, step in enumerate(steps, 1):
                status_icon = "✅" if step.get('status') == 'completed' else "❌" if step.get('status') == 'failed' else "⏳"
                print(f"  {status_icon} Step {i}: {step.get('node_type')} - {step.get('status')}")
                
                if step.get('output_data'):
                    output = step['output_data']
                    if isinstance(output, dict):
                        if 'file_info' in output:  # Drive write step
                            file_info = output['file_info']
                            print(f"      📁 File: {file_info.get('filename')}")
                            print(f"      📂 Folder: {file_info.get('folder_id')}")
                            print(f"      📊 Size: {file_info.get('size')} bytes")
                            print(f"      ⏱️ Status: {output.get('status')}")
                        elif 'data' in output:  # Sheets read step
                            data_count = len(output.get('data', []))
                            print(f"      📊 Records read: {data_count}")
                            if data_count > 0:
                                sample = output['data'][:2]  # Show first 2 records
                                print(f"      📋 Sample: {sample}")
                
                if step.get('logs'):
                    important_logs = [log for log in step['logs'] 
                                    if any(keyword in log.lower() for keyword in 
                                          ['success', 'error', 'file', 'upload', 'read'])][:2]
                    for log in important_logs:
                        print(f"      📝 {log}")
        
        return instance['status'] == 'completed'
    
    return False

def test_component_availability():
    """Test that both components are available"""
    
    print("🔧 Checking component availability...")
    
    components_response = requests.get("http://localhost:8000/api/v1/workflow/components")
    if components_response.status_code != 200:
        print(f"❌ Failed to get components: {components_response.text}")
        return False
    
    components = components_response.json()["data"]
    
    # Check for required components
    available_types = [comp["type"] for comp in components]
    required_components = ["google_sheets", "google_drive_write"]
    
    print(f"📦 Available components: {len(components)}")
    
    for comp_type in required_components:
        if comp_type in available_types:
            comp = next(c for c in components if c["type"] == comp_type)
            print(f"✅ {comp['name']} - {len(comp.get('parameters', []))} parameters")
        else:
            print(f"❌ Missing: {comp_type}")
            return False
    
    return True

if __name__ == "__main__":
    print("=== Sheets to Drive Workflow Integration Test ===\n")
    
    # Test 1: Component availability
    if not test_component_availability():
        print("\n❌ Component availability check failed")
        exit(1)
    
    # Test 2: Full workflow
    print("\n" + "="*60)
    success = test_sheets_to_drive_workflow()
    
    if success:
        print("\n🎉 Workflow integration test completed successfully!")
        print("\n📋 Summary:")
        print("✅ Template created")
        print("✅ Instance created") 
        print("✅ Workflow executed")
        print("✅ Data processed")
        print("✅ File uploaded (simulated)")
        print("\n💡 Note: Upload is simulated due to Google Drive service account limitations")
        print("   In production, use OAuth delegation or Shared Drives for real uploads")
    else:
        print("\n❌ Workflow integration test failed")
        print("Check the execution logs above for details")
