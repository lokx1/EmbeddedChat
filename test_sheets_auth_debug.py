#!/usr/bin/env python3
"""
Test Google Sheets Write Component Authentication
"""

import requests
import json
from datetime import datetime

def test_sheets_write_auth():
    """Test Google Sheets Write component with authentication debugging"""
    print("🔐 TESTING GOOGLE SHEETS WRITE AUTHENTICATION")
    print("="*55)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Simple workflow with just trigger -> sheets write
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
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "Write Test Data",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "Auth_Test",
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
                "source": "trigger-1",
                "target": "sheets-write-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # Test data that should be written
    test_data = [
        ["Header 1", "Header 2", "Header 3", "Header 4", "Header 5", "Prompt Column"],
        ["Data 1", "Data 2", "Data 3", "Success", "Generated URL", "This is AI response text for testing"],
        ["Data A", "Data B", "Data C", "Success", "Another URL", "Another AI response text here"]
    ]
    
    input_data = {
        "data": test_data
    }
    
    # Create workflow
    save_payload = {
        "name": f"Auth Test - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Test Google Sheets authentication",
        "workflow_data": workflow_data,
        "category": "auth_test"
    }
    
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"✅ Template created: {template_id}")
        
        # Create instance
        instance_payload = {
            "template_id": template_id,
            "name": f"Auth Test Instance - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": input_data
        }
        
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            print(f"✅ Instance created: {instance_id}")
            
            # Execute
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            
            if execute_response.status_code == 200:
                print("✅ Execution started")
                
                import time
                time.sleep(5)
                
                # Get logs with detailed debugging
                logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                if logs_response.status_code == 200:
                    logs_data = logs_response.json()
                    steps = logs_data.get("data", {}).get("steps", [])
                    
                    for step in steps:
                        if step['step_type'] == 'google_sheets_write':
                            print(f"\n📊 GOOGLE SHEETS WRITE STEP:")
                            print(f"   Status: {step['status']}")
                            
                            if step.get('error_message'):
                                print(f"   ❌ Error: {step['error_message']}")
                            
                            if step.get('logs'):
                                print(f"   📝 Detailed logs:")
                                for log in step['logs']:
                                    print(f"      - {log}")
                            
                            if step.get('output_data'):
                                output_data = step['output_data']
                                print(f"   📊 Output data:")
                                print(f"      Operation: {output_data.get('operation', 'N/A')}")
                                print(f"      Status: {output_data.get('status', 'N/A')}")
                                
                                if output_data.get('status') == 'simulated':
                                    print(f"   ⚠️  RUNNING IN SIMULATION MODE!")
                                    print(f"      This means authentication or API call failed")
                                elif output_data.get('status') == 'success':
                                    print(f"   ✅ REAL WRITE SUCCESS!")
                                    print(f"      Rows written: {output_data.get('data_written', {}).get('rows_count', 'N/A')}")
                
                # Get final status
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data["data"]["instance"]
                    
                    print(f"\n📊 Final Status: {instance['status']}")
                    
                    if instance.get('output_data', {}).get('node_outputs', {}).get('sheets-write-1'):
                        sheets_output = instance['output_data']['node_outputs']['sheets-write-1']
                        print(f"📊 Final Sheets Output:")
                        print(f"   Operation: {sheets_output.get('operation', 'N/A')}")
                        print(f"   Status: {sheets_output.get('status', 'N/A')}")
                        
                        if sheets_output.get('status') == 'success':
                            print(f"🎉 SUCCESS! Data was written to Google Sheets!")
                            return True
                        else:
                            print(f"❌ FAILED: Data was not written (simulation mode)")
                            return False
    
    return False

if __name__ == "__main__":
    success = test_sheets_write_auth()
    
    if success:
        print(f"\n🎉 AUTHENTICATION WORKING!")
        print(f"📊 Your AI_Response data should now be in Google Sheets")
    else:
        print(f"\n❌ AUTHENTICATION ISSUE")
        print(f"💡 Google Sheets Write is running in simulation mode")
        print(f"🔧 Need to fix authentication in component")
