#!/usr/bin/env python3
"""
Test frontend-like workflow with Google Sheets Read + Write
"""

import requests
import json
from datetime import datetime

def test_frontend_workflow():
    """Test workflow similar to what frontend creates"""
    base_url = "http://localhost:8000/api/v1"
    
    # Use your real Google Sheets ID
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    print(f"🔍 Testing frontend-like workflow with sheet: {sheet_id}")
    
    # Create workflow similar to frontend
    workflow_data = {
        "nodes": [
            {
                "id": "start-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "config": {}
                }
            },
            {
                "id": "sheets-read-2",
                "type": "google_sheets",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "Google Sheets",
                    "type": "google_sheets",
                    "config": {
                        "sheet_id": sheet_id,
                        "sheet_name": "Trang tính1",  # Use correct Vietnamese sheet name
                        "range": "A1:E10"
                    }
                }
            },
            {
                "id": "ai-process-3",
                "type": "ai_processing",
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "AI Processing",
                    "type": "ai_processing",
                    "config": {
                        "model": "qwen3:8b",
                        "prompt": "Based on this asset request: {input}\\nGenerate a comprehensive asset request:\\n{input}",
                        "temperature": 0.3,
                        "max_tokens": 300
                    }
                }
            },
            {
                "id": "write-results-4",
                "type": "google_sheets_write",
                "position": {"x": 700, "y": 100},
                "data": {
                    "label": "Write Results",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": sheet_id,
                        "sheet_name": "Results",  # Write to Results sheet
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
                "source": "start-1",
                "target": "sheets-read-2",
                "sourceHandle": "output",
                "targetHandle": "input"
            },
            {
                "id": "edge-2",
                "source": "sheets-read-2",
                "target": "ai-process-3",
                "sourceHandle": "output",
                "targetHandle": "input"
            },
            {
                "id": "edge-3",
                "source": "ai-process-3",
                "target": "write-results-4",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # Save workflow template
    save_payload = {
        "name": f"Frontend Workflow Test - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Test workflow similar to frontend: Read → AI → Write",
        "workflow_data": workflow_data,
        "category": "frontend_test"
    }
    
    print("🚀 Creating frontend-like workflow...")
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
            "name": f"Frontend Test - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": {}  # No input data - should read from sheets
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
                
                # Monitor execution
                import time
                for i in range(10):  # Wait up to 30 seconds
                    time.sleep(3)
                    
                    status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        instance = status_data["data"]["instance"]
                        
                        print(f"\\n📋 Status check {i+1}: {instance['status']}")
                        
                        if instance['status'] in ['completed', 'failed', 'error']:
                            break
                            
                        # Show progress
                        if instance.get('output_data') and 'node_outputs' in instance['output_data']:
                            outputs = instance['output_data']['node_outputs']
                            for node_id, output in outputs.items():
                                print(f"   {node_id}: {output.get('status', 'unknown')}")
                
                # Final status check
                print(f"\\n📋 Final Status: {instance['status']}")
                
                if instance.get('output_data'):
                    output = instance['output_data']
                    print("\\n📤 Final Results:")
                    
                    if 'node_outputs' in output:
                        for node_id, node_output in output['node_outputs'].items():
                            print(f"\\n🔹 {node_id}:")
                            print(f"   Status: {node_output.get('status', 'unknown')}")
                            if node_output.get('operation'):
                                print(f"   Operation: {node_output.get('operation')}")
                            if node_output.get('error'):
                                print(f"   Error: {node_output.get('error')}")
                
                if instance.get('error_message'):
                    print(f"\\n❌ Workflow Error: {instance['error_message']}")
                
                # Get execution logs
                logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                if logs_response.status_code == 200:
                    logs_data = logs_response.json()
                    steps = logs_data.get("data", {}).get("steps", [])
                    
                    print(f"\\n📝 Execution Steps ({len(steps)}):")
                    for step in steps:
                        print(f"   [{step['created_at']}] {step['step_type']}: {step['status']}")
                        if step.get('error_message'):
                            print(f"      ❌ {step['error_message']}")
                
                return instance['status'] == 'completed'
                
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
    print("=== Frontend Workflow Test ===\\n")
    
    success = test_frontend_workflow()
    
    if success:
        print("\\n🎉 Frontend workflow test successful!")
        print("\\nThis means:")
        print("✅ Google Sheets Read works")
        print("✅ AI Processing works") 
        print("✅ Google Sheets Write works")
        print("✅ Data flows correctly between components")
    else:
        print("\\n❌ Frontend workflow test failed")
        print("Check the logs above for specific errors")
