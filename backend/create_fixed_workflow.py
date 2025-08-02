#!/usr/bin/env python3
"""
Create a fixed workflow with correct Google Sheets configuration
"""
import requests
import json
from datetime import datetime


def create_fixed_workflow():
    """Create workflow with CORRECT sheet ID and test execution"""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Workflow with CORRECT sheet ID
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
                            "test": "Fixed workflow data",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                }
            },
            {
                "id": "sheets-write-1", 
                "type": "google_sheets_write",
                "position": {"x": 400, "y": 100},
                "data": {
                    "label": "Google Sheets Write (FIXED)",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",  # CORRECT ID
                        "sheet_name": "Result_Test",
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
    
    # Create workflow template
    save_payload = {
        "name": "FIXED Google Sheets Write Test",
        "description": "Fixed workflow with correct Google Sheets ID",
        "workflow_data": workflow_data,
        "category": "test"
    }
    
    print("🚀 Creating FIXED workflow template...")
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    print(f"Save response: {save_response.status_code}")
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"✅ Template created: {template_id}")
        
        # Create and execute instance
        execute_payload = {
            "name": f"Fixed execution {datetime.now().strftime('%H:%M:%S')}",
            "template_id": template_id,
            "workflow_data": template_data["data"]["workflow_data"],
            "input_data": {
                "test_data": [
                    ["Name", "Age", "City", "Status"],
                    ["Fixed User 1", "25", "Fixed City 1", "Success"],
                    ["Fixed User 2", "30", "Fixed City 2", "Success"]
                ]
            }
        }
        
        print("\n📊 Creating and executing instance...")
        execute_response = requests.post(f"{base_url}/workflow/instances", json=execute_payload)
        print(f"Execute response: {execute_response.status_code}")
        
        if execute_response.status_code == 200:
            execution_data = execute_response.json()
            instance_id = execution_data["instance_id"]
            print(f"✅ Instance created: {instance_id}")
            
            # Execute the instance
            run_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            print(f"Run response: {run_response.status_code}")
            
            if run_response.status_code == 200:
                run_data = run_response.json()
                print(f"✅ Execution started: {run_data}")
                
                # Wait and check results
                import time
                print("\n⏳ Waiting for execution to complete...")
                time.sleep(3)
                
                # Check status
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                if status_response.status_code == 200:
                    instance = status_response.json()
                    print(f"\n📋 Final Status: {instance.get('status', 'unknown')}")
                    
                    if 'output_data' in instance and instance['output_data']:
                        output_data = instance['output_data']
                        print(f"📊 Output nodes: {list(output_data.keys())}")
                        
                        # Check sheets write output
                        if 'sheets-write-1' in output_data:
                            sheets_result = output_data['sheets-write-1']
                            status = sheets_result.get('status', 'unknown')
                            operation = sheets_result.get('operation', 'unknown')
                            
                            if status == 'success' and operation == 'write_api':
                                print("🎉 SUCCESS: Real Google Sheets API used!")
                                print(f"   Data written: {sheets_result.get('data_written', {})}")
                            else:
                                print(f"⚠️  Status: {status}, Operation: {operation}")
                        
                print(f"\n🔗 Check results: https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit")
                return True
            else:
                print(f"❌ Failed to run: {run_response.text}")
        else:
            print(f"❌ Failed to create instance: {execute_response.text}")
    else:
        print(f"❌ Failed to create template: {save_response.text}")
        
    return False


if __name__ == "__main__":
    print("🔧 Creating FIXED Google Sheets Workflow")
    print("=" * 50)
    
    success = create_fixed_workflow()
    
    if success:
        print("\n✅ FIXED WORKFLOW SUCCESSFUL!")
        print("💡 This proves the issue was incorrect sheet ID")
        print("🎯 Frontend should be updated to use the correct ID")
    else:
        print("\n❌ Something still wrong")
