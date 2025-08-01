"""
Test Google Sheets workflow via API
"""
import requests
import json


def test_workflow_execution_via_api():
    """Test workflow execution through the REST API"""
    
    base_url = "http://localhost:8000/api/v1"
    
    print("🚀 Testing Google Sheets Workflow via API")
    print("=" * 50)
    
    try:
        # Test 1: Create a workflow instance 
        print("\n📋 Step 1: Creating workflow instance...")
        
        workflow_data = {
            "nodes": [
                {
                    "id": "trigger-1",
                    "type": "manual_trigger",
                    "position": {"x": 100, "y": 200},
                    "data": {
                        "label": "Start",
                        "type": "manual_trigger",
                        "parameters": {}
                    }
                },
                {
                    "id": "sheets-1",
                    "type": "google_sheets", 
                    "position": {"x": 400, "y": 200},
                    "data": {
                        "label": "Google Sheets Reader",
                        "type": "google_sheets",
                        "parameters": {
                            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                            "sheet_name": "Sheet1",
                            "range": "A1:Z1000"
                        }
                    }
                }
            ],
            "edges": [
                {
                    "id": "edge-1", 
                    "source": "trigger-1",
                    "target": "sheets-1",
                    "sourceHandle": "output",
                    "targetHandle": "input"
                }
            ],
            "viewport": {"x": 0, "y": 0, "zoom": 1}
        }
        
        instance_response = requests.post(
            f"{base_url}/workflow/instances",
            json={
                "name": "API Test - Google Sheets",
                "workflow_data": workflow_data
            },
            headers={"Content-Type": "application/json"}
        )
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            print(f"API Response: {json.dumps(instance_data, indent=2)}")
            instance_id = instance_data["instance_id"]  # Use correct key
            print(f"✅ Created workflow instance: {instance_id}")
        else:
            print(f"❌ Failed to create instance (status {instance_response.status_code})")
            print(f"Response: {instance_response.text}")
            return
            
        # Test 2: Execute the workflow
        print(f"\n🔧 Step 2: Executing workflow instance...")
        
        execute_response = requests.post(
            f"{base_url}/workflow/instances/{instance_id}/execute",
            json={"input_data": {}},
            headers={"Content-Type": "application/json"}
        )
        
        if execute_response.status_code == 200:
            execute_data = execute_response.json()
            print(f"✅ Execution started successfully")
            print(f"   Status: {execute_data.get('data', {}).get('status', 'unknown')}")
        else:
            print(f"❌ Failed to execute: {execute_response.text}")
            return
            
        # Test 3: Check execution status
        print(f"\n📊 Step 3: Checking execution status...")
        
        status_response = requests.get(
            f"{base_url}/workflow/instances/{instance_id}",
            headers={"Content-Type": "application/json"}
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            instance_info = status_data["data"]
            print(f"   Status: {instance_info.get('status', 'unknown')}")
            
            # Show output data if available
            output_data = instance_info.get('output_data')
            if output_data:
                print(f"   Output Data Available: {list(output_data.keys())}")
                
                # Check for Google Sheets data
                if 'sheets-1' in output_data:
                    sheets_result = output_data['sheets-1']
                    if 'records' in sheets_result:
                        records = sheets_result['records']
                        print(f"   Google Sheets Records: {len(records)}")
                        
                        if records:
                            print(f"\n📋 Sample Record:")
                            print(f"      {records[0]}")
                            
                    if 'spreadsheet_info' in sheets_result:
                        info = sheets_result['spreadsheet_info']
                        print(f"   Columns: {', '.join(info.get('columns', []))}")
                        
        else:
            print(f"❌ Failed to get status: {status_response.text}")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 API Test Complete")


if __name__ == "__main__":
    test_workflow_execution_via_api()
