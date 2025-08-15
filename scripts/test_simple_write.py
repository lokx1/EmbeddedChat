#!/usr/bin/env python3
"""
Test simple GoogleSheetsWrite with debug
"""

import requests
import json
from datetime import datetime

def test_simple_sheets_write():
    """Test GoogleSheetsWrite with known working data"""
    base_url = "http://localhost:8000/api/v1"
    
    # Use your real Google Sheets ID
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    # Create simple workflow - just trigger → write
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
                "id": "sheets-write-1",
                "type": "google_sheets_write",
                "position": {"x": 400, "y": 100},
                "data": {
                    "label": "Write Test",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": sheet_id,
                        "sheet_name": f"SimpleTest_{datetime.now().strftime('%H%M%S')}",  # New sheet name
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
        ["Date", "Test", "Status"],
        [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Simple Write Test", "SUCCESS"],
        [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "API Integration", "TESTING"]
    ]
    
    # Save workflow template
    save_payload = {
        "name": f"Simple Write Test - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Simple test to verify GoogleSheetsWrite API",
        "workflow_data": workflow_data,
        "category": "simple_test"
    }
    
    print("🚀 Creating simple write test...")
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    print(f"Save response: {save_response.status_code}")
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"✅ Template created with ID: {template_id}")
        
        # Create workflow instance with explicit data
        print("\\n📊 Creating workflow instance...")
        instance_payload = {
            "template_id": template_id,
            "name": f"Simple Write - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": {
                "data": test_data,  # Explicit data
                "test_data": test_data,  # Backup key
                "results_for_sheets": test_data  # AI-like key
            }
        }
        
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        print(f"Instance response: {instance_response.status_code}")
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            print(f"✅ Instance created with ID: {instance_id}")
            
            # Execute the workflow
            print("\\n🚀 Executing workflow...")
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            print(f"Execute response: {execute_response.status_code}")
            
            if execute_response.status_code == 200:
                print("✅ Workflow execution started")
                
                # Check status
                import time
                time.sleep(3)
                
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data["data"]["instance"]
                    
                    print(f"\\n📋 Final Status: {instance['status']}")
                    
                    if instance.get('output_data'):
                        output = instance['output_data']
                        
                        # Check Google Sheets Write result
                        if 'node_outputs' in output and 'sheets-write-1' in output['node_outputs']:
                            sheets_output = output['node_outputs']['sheets-write-1']
                            print(f"\\n✅ Google Sheets Write Result:")
                            print(f"   - Operation: {sheets_output.get('operation', 'N/A')}")
                            print(f"   - Status: {sheets_output.get('status', 'N/A')}")
                            print(f"   - Target Sheet: {sheets_output.get('sheet_info', {}).get('sheet_name', 'N/A')}")
                            print(f"   - Rows Written: {sheets_output.get('data_written', {}).get('rows_count', 'N/A')}")
                            
                            if sheets_output.get('status') == 'success':
                                print("\\n🎉 SUCCESS! Real Google Sheets API used!")
                                return True
                            elif sheets_output.get('status') == 'simulated':
                                print("\\n⚠️  Still in simulation mode")
                                
                                # Get detailed logs to debug
                                logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                                if logs_response.status_code == 200:
                                    logs_data = logs_response.json()
                                    steps = logs_data.get("data", {}).get("steps", [])
                                    
                                    for step in steps:
                                        if step['step_type'] == 'google_sheets_write':
                                            print(f"\\n🔍 Write step details:")
                                            if step.get('error_message'):
                                                print(f"   Error: {step['error_message']}")
                                            if step.get('output_data'):
                                                print(f"   Output keys: {list(step['output_data'].keys())}")
                                                
                                return False
                                
                    if instance.get('error_message'):
                        print(f"❌ Error: {instance['error_message']}")
                        
                    return False
                    
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
    print("=== Simple Google Sheets Write Test ===\\n")
    
    success = test_simple_sheets_write()
    
    if success:
        print("\\n🎉 Real Google Sheets API is working!")
    else:
        print("\\n❌ Still using simulation mode - need to debug further")
