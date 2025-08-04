#!/usr/bin/env python3
"""
Create workflow with specific worksheet name for AI to Sheets
"""

import requests
import json

def create_ai_to_sheets_workflow_with_worksheet():
    """Create workflow that writes to specific worksheet"""
    print("🚀 CREATING AI TO SHEETS WORKFLOW WITH WORKSHEET NAME")
    print("="*60)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Create workflow template with specific worksheet
    workflow_template = {
        "name": "AI to Sheets with Worksheet",
        "description": "AI Processing with Sheet Write to specific worksheet",
        "components": [
            {
                "id": "manual_trigger",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "config": {
                    "label": "Manual Trigger",
                    "type": "manual_trigger",
                    "configuration": {}
                }
            },
            {
                "id": "google_sheets",
                "type": "google_sheets",
                "position": {"x": 300, "y": 100},
                "config": {
                    "label": "Read Google Sheets",
                    "type": "google_sheets",
                    "configuration": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "worksheet_name": "TEST_NEW",  # Specify worksheet with Prompt column
                        "range": "A:Z"
                    }
                }
            },
            {
                "id": "ai_processing",
                "type": "ai_processing",
                "position": {"x": 500, "y": 100},
                "config": {
                    "label": "AI Processing",
                    "type": "ai_processing",
                    "configuration": {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.7,
                        "max_tokens": 1000,
                        "prompt_template": "Create a detailed prompt for: {{Description}}"
                    }
                }
            },
            {
                "id": "google_sheets_write",
                "type": "google_sheets_write",
                "position": {"x": 700, "y": 100},
                "config": {
                    "label": "Write to Google Sheets",
                    "type": "google_sheets_write",
                    "configuration": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "worksheet_name": "TEST_NEW",  # Same worksheet for write
                        "operation": "append"
                    }
                }
            }
        ],
        "connections": [
            {
                "source": "manual_trigger",
                "target": "google_sheets"
            },
            {
                "source": "google_sheets",
                "target": "ai_processing"
            },
            {
                "source": "ai_processing",
                "target": "google_sheets_write"
            }
        ]
    }
    
    try:
        # Create workflow template
        template_response = requests.post(
            f"{base_url}/workflow/templates",
            json=workflow_template
        )
        
        if template_response.status_code == 201:
            template_data = template_response.json()
            template_id = template_data["data"]["id"]
            print(f"✅ Created workflow template: {template_id}")
            
            # Create workflow instance
            instance_data = {
                "name": "AI to Sheets with Worksheet - " + 
                       __import__('datetime').datetime.now().strftime("%H:%M:%S"),
                "description": "Test AI processing with specific worksheet write",
                "template_id": template_id
            }
            
            instance_response = requests.post(
                f"{base_url}/workflow/instances",
                json=instance_data
            )
            
            if instance_response.status_code == 201:
                instance_resp_data = instance_response.json()
                instance_id = instance_resp_data["data"]["id"]
                print(f"✅ Created workflow instance: {instance_id}")
                
                # Execute workflow
                execute_response = requests.post(
                    f"{base_url}/workflow/instances/{instance_id}/execute"
                )
                
                if execute_response.status_code == 200:
                    print(f"🚀 Workflow execution started!")
                    
                    # Wait and check status
                    import time
                    max_wait = 30
                    wait_time = 0
                    
                    while wait_time < max_wait:
                        status_response = requests.get(
                            f"{base_url}/workflow/instances/{instance_id}"
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            status = status_data["data"]["status"]
                            
                            print(f"⏳ Status: {status} (waited {wait_time}s)")
                            
                            if status == "completed":
                                print(f"🎉 Workflow completed!")
                                
                                # Check results
                                logs_response = requests.get(
                                    f"{base_url}/workflow/instances/{instance_id}/logs"
                                )
                                
                                if logs_response.status_code == 200:
                                    logs_data = logs_response.json()
                                    steps = logs_data.get("data", {}).get("steps", [])
                                    
                                    for step in steps:
                                        if step['step_type'] == 'google_sheets_write':
                                            output = step.get('output_data', {})
                                            operation = output.get('operation')
                                            status = output.get('status')
                                            
                                            print(f"📝 Sheets Write: {operation} -> {status}")
                                            
                                            if status == 'success':
                                                data_written = output.get('data_written', {})
                                                rows_count = data_written.get('rows_count', 0)
                                                range_written = data_written.get('range_written', 'N/A')
                                                
                                                print(f"   ✅ Wrote {rows_count} rows to range {range_written}")
                                                print(f"   📍 Check worksheet: TEST_NEW")
                                
                                return instance_id
                                
                            elif status == "failed":
                                print(f"❌ Workflow failed!")
                                return None
                        
                        time.sleep(2)
                        wait_time += 2
                    
                    print(f"⏰ Timeout waiting for completion")
                    return instance_id
                
                else:
                    print(f"❌ Failed to execute workflow: {execute_response.status_code}")
                    return None
            
            else:
                print(f"❌ Failed to create instance: {instance_response.status_code}")
                return None
        
        else:
            print(f"❌ Failed to create template: {template_response.status_code}")
            return None
    
    except Exception as e:
        print(f"💥 Error: {e}")
        return None

if __name__ == "__main__":
    create_ai_to_sheets_workflow_with_worksheet()
