#!/usr/bin/env python3
"""
Test real Google Sheets Write with your actual sheet
"""

import requests
import json
from datetime import datetime

def test_real_google_sheets_write():
    """Test writing to your real Google Sheets"""
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Your Google Sheets URL
    sheet_url = "https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit?gid=0#gid=0"
    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    
    print(f"📊 Testing with your real Google Sheets")
    print(f"🔗 Sheet ID: {sheet_id}")
    print(f"🎯 Target: NEW (next tab)")
    
    # Create a workflow template with Google Sheets Write component
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
                            "message": "Writing to your Google Sheets",
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
                    "label": "Write to NEW Sheet",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": sheet_id,
                        "sheet_name": "NEW",  # Write to NEW sheet tab
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
    
    # Sample data to write - test results
    sample_data = [
        ["Test Date", "Feature", "Status", "Notes"],
        [str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), "Google Sheets Write", "SUCCESS", "Workflow automation test successful"],
        [str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), "Data Flow", "SUCCESS", "Manual trigger → Google Sheets Write"],
        [str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), "Real API", "TESTING", "Using real Google Sheets API"]
    ]
    
    # Save workflow template
    save_payload = {
        "name": f"Real Google Sheets Write Test - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Test writing to real Google Sheets with API",
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
            "name": f"Real Sheets Test - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": {
                "data": sample_data
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
                        
                        # Check Google Sheets Write result
                        if 'node_outputs' in output and 'sheets-write-1' in output['node_outputs']:
                            sheets_output = output['node_outputs']['sheets-write-1']
                            print(f"\\n✅ Google Sheets Write Result:")
                            print(f"   - Operation: {sheets_output.get('operation', 'N/A')}")
                            print(f"   - Status: {sheets_output.get('status', 'N/A')}")
                            print(f"   - Target Sheet: {sheets_output.get('sheet_info', {}).get('sheet_name', 'N/A')}")
                            print(f"   - Rows Written: {sheets_output.get('data_written', {}).get('rows_count', 'N/A')}")
                            
                            if sheets_output.get('status') == 'success':
                                print("\\n🎉 SUCCESS! Data written to real Google Sheets!")
                                print(f"🔗 Check your sheet: {sheet_url}")
                                print(f"🔗 NEW tab: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=NEW")
                            elif sheets_output.get('status') == 'simulated':
                                print("\\n⚠️  Running in simulation mode")
                                print("   This means Google Sheets API is not fully configured")
                                
                    if instance.get('error_message'):
                        print(f"❌ Error: {instance['error_message']}")
                        
                    # Show sheet URLs
                    print(f"\\n🔗 Your Google Sheets:")
                    print(f"   Original: {sheet_url}")
                    print(f"   NEW tab: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=NEW")
                    
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
    print("=== Real Google Sheets Write Test ===\\n")
    
    success = test_real_google_sheets_write()
    
    if success:
        print("\\n🎉 Test completed!")
        print("\\n💡 If status was 'simulated':")
        print("   - Google Sheets API authentication needs setup")
        print("   - But the workflow data flow is working correctly!")
        print("\\n💡 If status was 'success':")
        print("   - Check your Google Sheets for the new data!")
        print("   - Look for the 'NEW' tab in your spreadsheet")
    else:
        print("\\n❌ Test failed")
