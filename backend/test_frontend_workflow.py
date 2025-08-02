#!/usr/bin/env python3

import asyncio
import sys
import os
import json
import requests
from datetime import datetime

async def test_frontend_workflow():
    """Test the frontend workflow execution with the fix"""
    
    print("🧪 Testing Frontend Workflow with Fix")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Get the latest "Qwen AI Workflow" instance (from frontend)
    print("📋 Getting latest Qwen AI Workflow...")
    
    instances_response = requests.get(f"{base_url}/api/v1/workflow/instances")
    if instances_response.status_code != 200:
        print(f"❌ Failed to get instances: {instances_response.status_code}")
        return
    
    instances = instances_response.json()
    print(f"📋 Found {len(instances)} instances")
    
    # Handle different response formats
    if isinstance(instances, dict) and "data" in instances:
        instances = instances["data"]
    
    qwen_workflows = []
    for i in instances:
        if isinstance(i, dict) and "name" in i and "Qwen AI Workflow" in i["name"]:
            qwen_workflows.append(i)
    
    if not qwen_workflows:
        print("❌ No Qwen AI Workflow found")
        return
        
    latest_workflow = max(qwen_workflows, key=lambda x: x["created_at"])
    instance_id = latest_workflow["id"]
    
    print(f"✅ Found workflow: {latest_workflow['name']}")
    print(f"📋 Instance ID: {instance_id}")
    print(f"📊 Current Status: {latest_workflow['status']}")
    
    # Execute it again to test the fix
    print(f"\n📋 Executing workflow...")
    
    execute_response = requests.post(
        f"{base_url}/api/v1/workflow/instances/{instance_id}/execute",
        json={"input_data": {}}
    )
    
    if execute_response.status_code != 200:
        print(f"❌ Failed to execute workflow: {execute_response.status_code}")
        print(f"Response: {execute_response.text}")
        return
    
    print(f"✅ Execution started")
    execute_result = execute_response.json()
    print(f"📋 Response: {execute_result}")
    
    # Wait for completion
    print(f"\n📋 Waiting for completion...")
    
    for i in range(30):  # Wait up to 30 seconds
        await asyncio.sleep(1)
        
        status_response = requests.get(f"{base_url}/api/v1/workflow/instances/{instance_id}")
        if status_response.status_code == 200:
            instance = status_response.json()
            instance_data = instance.get("data", {}).get("instance", {})
            status = instance_data.get("status", "unknown")
            
            print(f"  Status: {status} ({i+1}s)")
            
            if status in ["completed", "failed", "cancelled"]:
                print(f"\n📊 Final Status: {status}")
                
                # Check execution steps via database
                print(f"📋 Checking execution details...")
                
                # Use requests to call a debug endpoint if available, or check database directly
                await check_execution_steps(instance_id)
                break
        else:
            print(f"  Failed to get status: {status_response.status_code}")
    else:
        print(f"\n⏰ Timeout waiting for completion")


async def check_execution_steps(instance_id):
    """Check execution steps for the workflow"""
    import sys
    import os
    
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from core.database import get_db
        from models.workflow import WorkflowExecutionStep
        from sqlalchemy.orm import Session
        
        db: Session = next(get_db())
        try:
            steps = db.query(WorkflowExecutionStep).filter(
                WorkflowExecutionStep.workflow_instance_id == instance_id
            ).order_by(WorkflowExecutionStep.created_at.desc()).limit(10).all()
            
            print(f"📋 Recent Execution Steps ({len(steps)}):")
            for step in steps:
                print(f"  {step.step_name} ({step.step_type}): {step.status}")
                if step.step_type == 'google_sheets_write':
                    print(f"    Error: {step.error_message}")
                    if step.output_data:
                        print(f"    Output: {step.output_data}")
                    else:
                        print(f"    Output: None")
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error checking steps: {e}")


if __name__ == "__main__":
    asyncio.run(test_frontend_workflow())
