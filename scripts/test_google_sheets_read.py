#!/usr/bin/env python3
"""
Test Google Sheets Read component
"""

import requests
import json
from datetime import datetime

def test_google_sheets_read():
    """Test workflow with Google Sheets Read component"""
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Your Google Sheets URL (same as before)
    sheet_url = "https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit?gid=0#gid=0"
    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    
    print(f"📊 Testing Google Sheets Read")
    print(f"🔗 Sheet ID: {sheet_id}")
    
    # Create workflow with Manual Trigger → Google Sheets Read
    workflow_data = {
        "nodes": [
            {
                "id": "start-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "config": {
                        "trigger_data": {
                            "message": "Reading from Google Sheets",
                            "timestamp": str(datetime.now())
                        }
                    }
                }
            },
            {
                "id": "sheets-read-1",
                "type": "google_sheets",
                "position": {"x": 400, "y": 100},
                "data": {
                    "label": "Google Sheets Read",
                    "type": "google_sheets",
                    "config": {
                        "sheet_id": sheet_id,
                        "sheet_name": "Trang tính1",  # Correct sheet name from your Google Sheets
                        "range": "A1:Z100",
                        "action": "read"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "start-1",
                "target": "sheets-read-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # Save workflow template
    save_payload = {
        "name": f"Google Sheets Read Test - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Test reading from Google Sheets",
        "workflow_data": workflow_data,
        "category": "google_sheets_test"
    }
    
    print("🚀 Creating workflow template...")
    save_response = requests.post(f"{base_url}/editor/save", json=save_payload)
    print(f"Save response: {save_response.status_code}")
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"✅ Template created with ID: {template_id}")
        
        # Create workflow instance
        print("📊 Creating workflow instance...")
        instance_payload = {
            "template_id": template_id,
            "name": f"Read Test - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": {
                "trigger": "read_test"
            }
        }
        
        instance_response = requests.post(f"{base_url}/instances", json=instance_payload)
        print(f"Instance response: {instance_response.status_code}")
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            print(f"✅ Instance created with ID: {instance_id}")
            
            # Execute the workflow
            print("🚀 Executing workflow...")
            execute_response = requests.post(f"{base_url}/instances/{instance_id}/execute")
            print(f"Execute response: {execute_response.status_code}")
            
            if execute_response.status_code == 200:
                print("✅ Workflow execution started")
                
                # Check status
                import time
                time.sleep(3)
                
                status_response = requests.get(f"{base_url}/instances/{instance_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data["data"]["instance"]
                    
                    print(f"\\n📋 Final Status: {instance['status']}")
                    
                    if instance.get('output_data'):
                        output = instance['output_data']
                        print("📤 Output Data:")
                        
                        # Check Google Sheets Read result
                        if 'node_outputs' in output and 'sheets-read-1' in output['node_outputs']:
                            read_output = output['node_outputs']['sheets-read-1']
                            print(f"\\n✅ Google Sheets Read Result:")
                            print(f"   - Status: {read_output.get('status', 'N/A')}")
                            print(f"   - Rows count: {read_output.get('rows_count', 'N/A')}")
                            print(f"   - Headers: {read_output.get('headers', [])}")
                            
                            if read_output.get('status') == 'success':
                                print("\\n🎉 SUCCESS! Data read from Google Sheets!")
                                data = read_output.get('data', [])
                                print(f"📊 Found {len(data)} rows")
                                if data:
                                    print("📝 First few rows:")
                                    for i, row in enumerate(data[:3]):
                                        print(f"   Row {i+1}: {row}")
                            else:
                                print(f"\\n⚠️  Read status: {read_output.get('status')}")
                                
                    if instance.get('error_message'):
                        print(f"❌ Error: {instance['error_message']}")
                        
                    # Get execution logs
                    logs_response = requests.get(f"{base_url}/instances/{instance_id}/logs")
                    if logs_response.status_code == 200:
                        logs_data = logs_response.json()
                        steps = logs_data.get("data", {}).get("steps", [])
                        
                        print(f"\\n📝 Execution Steps ({len(steps)}):")
                        for step in steps:
                            print(f"   [{step['step_type']}] {step['status']}")
                            if step.get('error_message'):
                                print(f"      Error: {step['error_message']}")
                    
                    return True
                    
            else:
                print(f"❌ Failed to execute: {execute_response.text}")
                return False
        else:
            print(f"❌ Failed to create instance: {instance_response.text}")
            return False
    else:
        print(f"❌ Failed to create template: {save_response.text}")
        return False

if __name__ == "__main__":
    print("=== Google Sheets Read Test ===\\n")
    
    success = test_google_sheets_read()
    
    if success:
        print("\\n🎉 Google Sheets Read test completed!")
    else:
        print("\\n❌ Test failed")
