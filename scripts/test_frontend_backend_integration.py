"""
Test Frontend to Backend integration for Google Sheets Write
"""

import requests
import json
from datetime import datetime

def test_frontend_backend_integration():
    """Test complete frontend to backend integration"""
    print("🌐 Testing Frontend to Backend Google Sheets Write Integration...")
    
    base_url = "http://localhost:8000/api/v1"
    
    # 1. Create workflow with both read and write components
    workflow_data = {
        "nodes": [
            {
                "id": "start-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "config": {}
                }
            },
            {
                "id": "sheets-read-2", 
                "type": "google_sheets",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "Read Sheet Data",
                    "type": "google_sheets",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "Trang tính1",
                        "range": "A1:Z"
                    }
                }
            },
            {
                "id": "sheets-write-3",
                "type": "google_sheets_write", 
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "Write to Results",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "FrontendResults",
                        "range": "A1",
                        "mode": "overwrite",
                        "data_format": "auto"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "start-1",
                "target": "sheets-read-2",
                "sourceHandle": "output",
                "targetHandle": "input"
            },
            {
                "id": "edge-2", 
                "source": "sheets-read-2",
                "target": "sheets-write-3",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # 2. Save workflow template
    save_payload = {
        "name": "Frontend Google Sheets Integration Test",
        "description": "Test read from one sheet and write to another via frontend",
        "workflow_data": workflow_data,
        "category": "frontend_test"
    }
    
    print("🚀 Creating workflow template...")
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"✅ Template created: {template_id}")
        
        # 3. Create workflow instance
        instance_payload = {
            "template_id": template_id,
            "name": f"Frontend Test {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": {}
        }
        
        print("\n📊 Creating workflow instance...")
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            print(f"✅ Instance created: {instance_id}")
            
            # 4. Execute workflow
            print("\n🚀 Executing workflow...")
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            
            if execute_response.status_code == 200:
                print("✅ Workflow execution started")
                
                # 5. Wait and check results
                import time
                time.sleep(5)  # Wait longer for read + write operations
                
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data["data"]["instance"]
                    
                    print(f"\n📋 Final Status: {instance['status']}")
                    
                    if instance.get('output_data'):
                        node_outputs = instance['output_data'].get('node_outputs', {})
                        
                        # Check read results
                        if 'sheets-read-2' in node_outputs:
                            read_output = node_outputs['sheets-read-2']
                            records = read_output.get('records', [])
                            print(f"📖 Read {len(records)} records from source sheet")
                        
                        # Check write results  
                        if 'sheets-write-3' in node_outputs:
                            write_output = node_outputs['sheets-write-3']
                            operation = write_output.get('operation')
                            status = write_output.get('status')
                            print(f"📝 Write operation: {operation}")
                            print(f"📊 Write status: {status}")
                            
                            if operation == 'write_success' and status == 'success':
                                print("🎉 SUCCESS! Frontend to Backend Google Sheets Write working!")
                                return True
                            else:
                                print(f"❌ Write failed: {write_output}")
                        
                    if instance.get('error_message'):
                        print(f"❌ Workflow error: {instance['error_message']}")
                        
                return False
            else:
                print(f"❌ Execution failed: {execute_response.text}")
        else:
            print(f"❌ Instance creation failed: {instance_response.text}")
    else:
        print(f"❌ Template creation failed: {save_response.text}")
        
    return False

if __name__ == "__main__":
    success = test_frontend_backend_integration()
    if success:
        print("\n✅ Frontend to Backend integration working!")
    else:
        print("\n❌ Frontend to Backend integration failed!")
