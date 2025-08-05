#!/usr/bin/env python3
"""
Debug Google Sheets Write Component
"""

import requests
import json
from datetime import datetime

def debug_sheets_write():
    """Debug the Google Sheets Write component execution"""
    print("🔍 DEBUGGING GOOGLE SHEETS WRITE COMPONENT")
    print("="*55)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Create a very simple workflow
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
    
    # Simple test data
    test_data = [
        ["Col1", "Col2", "Col3", "Status", "URL", "Prompt"],
        ["Value1", "Value2", "Value3", "Success", "https://test.com", "Test AI Response"],
    ]
    
    input_data = {
        "data": test_data
    }
    
    # Create workflow
    save_payload = {
        "name": f"Debug Test - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Debug Google Sheets write",
        "workflow_data": workflow_data,
        "category": "debug_test"
    }
    
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"✅ Template created: {template_id}")
        
        # Create instance
        instance_payload = {
            "template_id": template_id,
            "name": f"Debug Instance - {datetime.now().strftime('%H:%M:%S')}",
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
                time.sleep(3)
                
                # Get detailed logs
                logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                if logs_response.status_code == 200:
                    logs_data = logs_response.json()
                    steps = logs_data.get("data", {}).get("steps", [])
                    
                    for step in steps:
                        if step['step_type'] == 'google_sheets_write':
                            print(f"\n📊 GOOGLE SHEETS WRITE STEP DETAILS:")
                            print(f"   Status: {step['status']}")
                            print(f"   Start time: {step.get('start_time', 'N/A')}")
                            print(f"   End time: {step.get('end_time', 'N/A')}")
                            
                            # Check for errors
                            if step.get('error_message'):
                                print(f"   ❌ Error: {step['error_message']}")
                            
                            # Check detailed logs
                            if step.get('logs'):
                                print(f"   📝 Detailed logs:")
                                for log in step['logs']:
                                    print(f"      - {log}")
                                    # Look for GOOGLE_SHEETS_AVAILABLE log
                                    if "GOOGLE_SHEETS_AVAILABLE" in log:
                                        print(f"      🔍 FOUND: {log}")
                            
                            # Check output data
                            if step.get('output_data'):
                                output_data = step['output_data']
                                print(f"   📊 Output data:")
                                print(f"      Operation: {output_data.get('operation', 'N/A')}")
                                print(f"      Status: {output_data.get('status', 'N/A')}")
                                
                                if output_data.get('status') == 'simulated':
                                    print(f"   ⚠️  SIMULATION MODE DETECTED!")
                                    print(f"      This means the Google Sheets API is not working")
                                    
                                    # Let's check if there's an error in the output
                                    if 'error' in output_data:
                                        print(f"      Error in simulation: {output_data['error']}")
                                        
                                elif output_data.get('status') == 'success':
                                    print(f"   ✅ REAL WRITE SUCCESS!")
                                    print(f"      Rows written: {output_data.get('data_written', {}).get('rows_count', 'N/A')}")
                                    return True
                
                print(f"\n🔍 Let's check what the raw execution result looks like...")
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data["data"]["instance"]
                    
                    print(f"📊 Final Instance Status: {instance['status']}")
                    
                    if instance.get('output_data', {}).get('node_outputs', {}).get('sheets-write-1'):
                        sheets_output = instance['output_data']['node_outputs']['sheets-write-1']
                        print(f"📊 Final Sheets Output:")
                        print(f"   Operation: {sheets_output.get('operation', 'N/A')}")
                        print(f"   Status: {sheets_output.get('status', 'N/A')}")
                        
                        # Check if there's an error
                        if 'error' in sheets_output:
                            print(f"   ❌ Error found: {sheets_output['error']}")
    
    return False

if __name__ == "__main__":
    success = debug_sheets_write()
    
    if success:
        print(f"\n🎉 Google Sheets Write is working!")
    else:
        print(f"\n❌ Google Sheets Write is in simulation mode")
        print(f"💡 Need to debug the authentication or API call")
