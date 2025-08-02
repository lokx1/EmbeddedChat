#!/usr/bin/env python3

import asyncio
import sys
import os
import json
import requests
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def test_workflow_with_fix():
    """Test workflow execution with the fixed GoogleSheetsWriteComponent"""
    
    print("🧪 Testing Workflow with Fixed GoogleSheetsWriteComponent")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Step 1: Create a new workflow instance
    print("📋 Step 1: Creating workflow instance...")
    
    workflow_data = {
        "nodes": [
            {
                "id": "manual-trigger-1",
                "type": "manual_trigger",
                "data": {
                    "label": "Start Workflow",
                    "config": {}
                },
                "position": {"x": 100, "y": 100}
            },
            {
                "id": "sheets-read-2",
                "type": "google_sheets_read",
                "data": {
                    "label": "Read Test Data",
                    "config": {
                        "sheet_id": "1WjySc8DxYoPJf3gJtyPXUJpRfdFza",
                        "sheet_name": "Result_Test",
                        "range": "A1:B10"
                    }
                },
                "position": {"x": 300, "y": 100}
            },
            {
                "id": "ai-processing-3",
                "type": "ai_processing",
                "data": {
                    "label": "AI Processing",
                    "config": {
                        "provider": "ollama",
                        "model": "qwen3:8b",
                        "prompt": "Generate a test URL for this asset: {description}",
                        "temperature": 0.7,
                        "max_tokens": 100
                    }
                },
                "position": {"x": 500, "y": 100}
            },
            {
                "id": "sheets-write-4",
                "type": "google_sheets_write",
                "data": {
                    "label": "Write Results",
                    "config": {
                        "sheet_id": "1WjySc8DxYoPJf3gJtyPXUJpRfdFza",
                        "sheet_name": "Test",
                        "range": "A1",
                        "mode": "overwrite",
                        "data_format": "auto"
                    }
                },
                "position": {"x": 700, "y": 100}
            }
        ],
        "edges": [
            {
                "id": "e1",
                "source": "manual-trigger-1",
                "target": "sheets-read-2",
                "sourceHandle": "trigger",
                "targetHandle": "input"
            },
            {
                "id": "e2",
                "source": "sheets-read-2",
                "target": "ai-processing-3",
                "sourceHandle": "data",
                "targetHandle": "input"
            },
            {
                "id": "e3",
                "source": "ai-processing-3",
                "target": "sheets-write-4",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ]
    }
    
    create_response = requests.post(
        f"{base_url}/api/v1/workflow/instances",
        json={
            "name": f"Fixed Data Flow Test - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data
        }
    )
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create workflow: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return
    
    instance_data = create_response.json()
    print(f"📋 Response: {instance_data}")
    
    # Handle different response formats
    if "id" in instance_data:
        instance_id = instance_data["id"]
    elif "instance_id" in instance_data:
        instance_id = instance_data["instance_id"]
    else:
        print(f"❌ No instance ID found in response")
        return
        
    print(f"✅ Created instance: {instance_id}")
    
    # Step 2: Execute the workflow
    print(f"\n📋 Step 2: Executing workflow...")
    
    execute_response = requests.post(
        f"{base_url}/api/v1/workflow/instances/{instance_id}/execute",
        json={"input_data": {}}
    )
    
    if execute_response.status_code != 200:
        print(f"❌ Failed to execute workflow: {execute_response.status_code}")
        print(f"Response: {execute_response.text}")
        return
    
    print(f"✅ Execution started")
    
    # Step 3: Wait and check result
    print(f"\n📋 Step 3: Waiting for completion...")
    await asyncio.sleep(10)  # Wait for execution
    
    # Check final status
    status_response = requests.get(f"{base_url}/api/v1/workflow/instances/{instance_id}")
    if status_response.status_code == 200:
        instance = status_response.json()
        print(f"� Instance data: {instance}")
        print(f"�📊 Final Status: {instance.get('status', 'unknown')}")
        
        if instance.get('output_data'):
            print(f"📈 Has output data: YES")
        else:
            print(f"📈 Has output data: NO")
            
        # Check execution steps
        steps_response = requests.get(f"{base_url}/api/v1/workflow/instances/{instance_id}/steps")
        if steps_response.status_code == 200:
            steps = steps_response.json()
            print(f"\n📋 Execution Steps:")
            for step in steps:
                print(f"  {step.get('step_name', 'Unknown')} ({step.get('step_type', 'Unknown')}): {step.get('status', 'Unknown')}")
                if step.get('step_type') == 'google_sheets_write':
                    print(f"    Success: {step.get('success', False)}")
                    print(f"    Logs: {step.get('logs', [])}")
                    if step.get('error_message'):
                        print(f"    Error: {step['error_message']}")
        else:
            print(f"❌ Failed to get steps: {steps_response.status_code}")
    else:
        print(f"❌ Failed to get status: {status_response.status_code}")
    
    print(f"\n🏁 Test completed!")


if __name__ == "__main__":
    asyncio.run(test_workflow_with_fix())
