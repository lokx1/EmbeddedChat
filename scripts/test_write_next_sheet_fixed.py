#!/usr/bin/env python3
"""
Test writing to next sheet tab in Google Sheets - FIXED VERSION
URL: https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit?gid=0#gid=0
"""

import requests
import json
from datetime import datetime

def test_write_to_next_sheet():
    """Test writing to a new sheet tab"""
    base_url = "http://localhost:8000/api/v1"
    
    # Extract sheet ID from URL
    sheet_url = "https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit?gid=0#gid=0"
    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    
    print(f"📊 Sheet ID: {sheet_id}")
    print(f"🌐 Original URL: {sheet_url}")
    
    # Sample data to write
    sample_data = [
        ["Timestamp", "Action", "Status", "Notes"],
        [str(datetime.now()), "Test Write", "Success", "Written from workflow"],
        [str(datetime.now()), "Data Entry", "Pending", "Sample data entry"],
        [str(datetime.now()), "Validation", "Complete", "Data validated"]
    ]
    
    # Create a workflow template with Google Sheets Write component for new sheet
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
                        "trigger_data": {
                            "message": "Writing to next sheet tab",
                            "timestamp": str(datetime.now())
                        }
                    }
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
                        "sheet_name": "Sheet2",  # Write to Sheet2 (next tab)
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
        "name": "Write to Next Sheet Tab",
        "description": f"Write data to Sheet2 in document {sheet_id}",
        "workflow_data": workflow_data,
        "category": "google_sheets_test"
    }
    
    print("\n🚀 Creating workflow template...")
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    print(f"Save response: {save_response.status_code}")
    
    if save_response.status_code != 200:
        print(f"❌ Failed to create template: {save_response.text}")
        return False
    
    template_data = save_response.json()
    template_id = template_data["data"]["workflow_id"]
    print(f"✅ Template created with ID: {template_id}")
    
    # Create workflow instance from template
    print("\n📝 Creating workflow instance...")
    instance_payload = {
        "template_id": template_id,
        "name": f"Write to Sheet2 - {datetime.now().strftime('%H:%M:%S')}",
        "input_data": {
            "data": sample_data
        }
    }
    
    instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
    print(f"Instance response: {instance_response.status_code}")
    
    if instance_response.status_code != 200:
        print(f"❌ Failed to create instance: {instance_response.text}")
        return False
    
    instance_data = instance_response.json()
    instance_id = instance_data["data"]["id"]
    print(f"✅ Instance created with ID: {instance_id}")
    
    # Execute the workflow instance
    print("\n🚀 Executing workflow instance...")
    execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute", json={
        "input_data": {
            "data": sample_data
        }
    })
    print(f"Execute response: {execute_response.status_code}")
    
    if execute_response.status_code != 200:
        print(f"❌ Failed to execute workflow: {execute_response.text}")
        return False
    
    print(f"✅ Workflow execution completed successfully")
    
    # Check execution status
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
        
        # Show the direct URL to the new sheet
        sheet2_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=1"
        print(f"\n🔗 Expected Sheet2 URL: {sheet2_url}")
                
        return True
    else:
        print(f"❌ Failed to get status: {status_response.text}")
        return False

def test_multiple_sheet_options():
    """Test workflow with multiple sheet name options"""
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    sheet_names = ["Sheet2", "Results", "Data_Output", "NewSheet"]
    
    print("\n🔧 Testing multiple sheet name options...")
    
    for sheet_name in sheet_names:
        print(f"\n📊 Testing sheet name: '{sheet_name}'")
        
        # Create simple test data
        test_data = [
            ["Test", "Sheet", "Data"],
            [sheet_name, str(datetime.now()), "Sample"]
        ]
        
        # Simulate component execution
        config = {
            "sheet_id": sheet_id,
            "sheet_name": sheet_name,
            "range": "A1",
            "mode": "append",
            "data_format": "auto"
        }
        
        result = {
            "operation": "write",
            "sheet_info": config,
            "data_written": {
                "rows_count": len(test_data),
                "columns_count": len(test_data[0]) if test_data else 0
            },
            "status": "simulated"
        }
        
        print(f"  ✅ Config: {json.dumps(config, indent=4)}")
        print(f"  📝 Result: {json.dumps(result, indent=4)}")

if __name__ == "__main__":
    print("=== Google Sheets Write to Next Tab Test ===\n")
    
    # Test 1: Write to next sheet tab
    success = test_write_to_next_sheet()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed")
    
    # Test 2: Multiple sheet options
    test_multiple_sheet_options()
    
    print("\n📌 Note: This is currently a simulation.")
    print("📌 To write to actual Google Sheets, you need:")
    print("   1. Google Sheets API credentials")
    print("   2. OAuth authentication")  
    print("   3. Write permissions to the document")
    print("\n🔗 Your original sheet: https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit?gid=0#gid=0")
    print("🔗 Potential Sheet2: https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit#gid=1")
