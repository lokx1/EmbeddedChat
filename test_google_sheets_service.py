#!/usr/bin/env python3
"""
Test Google Sheets Service Authentication
"""

import requests
import json

def test_google_sheets_service():
    """Test Google Sheets service directly"""
    print("🔍 TESTING GOOGLE SHEETS SERVICE AUTHENTICATION")
    print("="*55)
    
    # Test if credentials exist
    import os
    creds_path = os.path.join(os.path.dirname(__file__), "backend", "credentials.json")
    print(f"📁 Credentials path: {creds_path}")
    
    if os.path.exists(creds_path):
        print(f"✅ Credentials file exists")
        
        # Check if it's valid JSON
        try:
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
            print(f"✅ Credentials file is valid JSON")
            print(f"📊 Service account email: {creds_data.get('client_email', 'N/A')}")
            print(f"📊 Project ID: {creds_data.get('project_id', 'N/A')}")
        except Exception as e:
            print(f"❌ Credentials file is not valid JSON: {e}")
            return False
    else:
        print(f"❌ Credentials file not found")
        return False
    
    # Test Google Sheets API directly
    print(f"\n🔧 Testing Google Sheets API via backend endpoint...")
    
    # Use the backend API to test Google Sheets
    base_url = "http://localhost:8000/api/v1"
    
    # Create a simple test workflow that should write to sheets
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
    
    # Test data
    test_data = [
        ["Test", "Authentication", "Prompt"],
        ["Working", "Success", "This should work now"]
    ]
    
    input_data = {
        "data": test_data
    }
    
    # Create and execute workflow
    save_payload = {
        "name": "Auth Test Direct",
        "description": "Direct authentication test",
        "workflow_data": workflow_data,
        "category": "auth_test"
    }
    
    try:
        save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
        
        if save_response.status_code == 200:
            template_data = save_response.json()
            template_id = template_data["data"]["workflow_id"]
            print(f"✅ Template created: {template_id}")
            
            instance_payload = {
                "template_id": template_id,
                "name": "Auth Test Instance Direct",
                "workflow_data": workflow_data,
                "input_data": input_data
            }
            
            instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
            
            if instance_response.status_code == 200:
                instance_data = instance_response.json()
                instance_id = instance_data["instance_id"]
                print(f"✅ Instance created: {instance_id}")
                
                execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
                
                if execute_response.status_code == 200:
                    print("✅ Execution started")
                    
                    import time
                    time.sleep(4)
                    
                    # Get very detailed logs
                    logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                    if logs_response.status_code == 200:
                        logs_data = logs_response.json()
                        steps = logs_data.get("data", {}).get("steps", [])
                        
                        for step in steps:
                            if step['step_type'] == 'google_sheets_write':
                                print(f"\n📊 DETAILED GOOGLE SHEETS STEP:")
                                
                                if step.get('logs'):
                                    print(f"   📝 All logs:")
                                    for i, log in enumerate(step['logs']):
                                        print(f"      {i+1}. {log}")
                                        
                                        # Look for specific debug info
                                        if "GOOGLE_SHEETS_AVAILABLE" in log:
                                            print(f"         🔍 Google Sheets Available: {log}")
                                        elif "Google Sheets API result" in log:
                                            print(f"         🔍 API Result: {log}")
                                        elif "authentication" in log.lower():
                                            print(f"         🔍 Auth Info: {log}")
                                        elif "error" in log.lower():
                                            print(f"         ❌ Error Info: {log}")
                                
                                if step.get('output_data'):
                                    output = step['output_data']
                                    print(f"   📊 Output Details:")
                                    print(f"      Operation: {output.get('operation', 'N/A')}")
                                    print(f"      Status: {output.get('status', 'N/A')}")
                                    if 'error' in output:
                                        print(f"      Error: {output['error']}")
                    
                    return True
                    
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    return False

if __name__ == "__main__":
    test_google_sheets_service()
