#!/usr/bin/env python3
"""
Test creating new Google Sheets with workflow
"""

import requests
import json
from datetime import datetime

def test_create_new_sheet_workflow():
    """Test creating and writing to a new Google Sheets tab"""
    base_url = "http://localhost:8000/api/v1"
    
    # Use your real Google Sheets ID
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    new_sheet_name = f"AutoCreated_{datetime.now().strftime('%H%M%S')}"
    
    print(f"🆕 Creating workflow to create new sheet: {new_sheet_name}")
    
    # Create workflow with Google Sheets Write to new tab
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
                    "label": f"Create {new_sheet_name}",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": sheet_id,
                        "sheet_name": new_sheet_name,  # New sheet name
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
    
    # Sample data for the new sheet
    sample_data = [
        ["Date", "Task", "Status", "Notes"],
        [datetime.now().strftime('%Y-%m-%d'), "Create New Sheet", "SUCCESS", "Automatically created via workflow"],
        [datetime.now().strftime('%Y-%m-%d'), "Write Test Data", "SUCCESS", "Test data written successfully"],
        [datetime.now().strftime('%Y-%m-%d'), "Verify Integration", "PENDING", "Manual verification needed"]
    ]
    
    # Save workflow template
    save_payload = {
        "name": f"Create New Sheet: {new_sheet_name}",
        "description": f"Workflow to create and populate new sheet: {new_sheet_name}",
        "workflow_data": workflow_data,
        "category": "google_sheets_auto"
    }
    
    print("🚀 Creating workflow template...")
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    print(f"Save response: {save_response.status_code}")
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"✅ Template created with ID: {template_id}")
        
        # Create workflow instance
        print("\\n📊 Creating workflow instance...")
        instance_payload = {
            "template_id": template_id,
            "name": f"New Sheet Creation - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": {
                "data": sample_data
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
                
                # Check status after execution
                import time
                time.sleep(3)
                
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data["data"]["instance"]
                    
                    print(f"\\n📋 Final Status: {instance['status']}")
                    
                    if instance.get('output_data'):
                        output = instance['output_data']
                        print("📤 Output Data:")
                        
                        # Check Google Sheets Write result
                        if 'node_outputs' in output and 'sheets-write-1' in output['node_outputs']:
                            sheets_output = output['node_outputs']['sheets-write-1']
                            print(f"\\n✅ Google Sheets Write Result:")
                            print(f"   - Operation: {sheets_output.get('operation', 'N/A')}")
                            print(f"   - Status: {sheets_output.get('status', 'N/A')}")
                            print(f"   - Target Sheet: {sheets_output.get('sheet_info', {}).get('sheet_name', 'N/A')}")
                            print(f"   - Rows Written: {sheets_output.get('data_written', {}).get('rows_count', 'N/A')}")
                            
                            if sheets_output.get('status') == 'success':
                                print("\\n🎉 SUCCESS! New sheet created and data written!")
                                print(f"🔗 Check your sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")
                                print(f"🔗 New tab: {new_sheet_name}")
                            elif sheets_output.get('status') == 'simulated':
                                print("\\n⚠️  Running in simulation mode")
                                print("   Real API would create the new sheet")
                                
                    if instance.get('error_message'):
                        print(f"❌ Error: {instance['error_message']}")
                        
                    # Get execution logs
                    logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                    if logs_response.status_code == 200:
                        logs_data = logs_response.json()
                        steps = logs_data.get("data", {}).get("steps", [])
                        
                        print(f"\\n📝 Execution Steps ({len(steps)}):")
                        for step in steps:
                            print(f"   [{step['created_at']}] {step['step_type']}: {step['status']}")
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
    print("=== Create New Google Sheets Test ===\\n")
    
    success = test_create_new_sheet_workflow()
    
    if success:
        print("\\n🎉 Test completed!")
        print("\\n💡 If the workflow succeeded:")
        print("   - A new sheet tab was created in your Google Sheets")
        print("   - Test data was written to the new tab")
        print("   - Check your Google Sheets to verify!")
    else:
        print("\\n❌ Test failed")
