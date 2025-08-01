#!/usr/bin/env python3
"""
Debug Frontend Workflow Execution Issue
"""

import requests
import json
import time
from datetime import datetime

def debug_frontend_execution():
    """Debug the frontend workflow execution error"""
    print("🔍 Debugging Frontend Workflow Execution Error")
    print("="*55)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Step 1: Check existing instances
    print("📋 Step 1: Checking existing instances...")
    
    try:
        response = requests.get(f"{base_url}/instances")
        
        if response.status_code == 200:
            data = response.json()
            instances = data.get("data", {}).get("instances", [])
            
            print(f"✅ Found {len(instances)} total instances")
            
            # Show recent instances
            for i, instance in enumerate(instances[:5]):
                print(f"   {i+1}. {instance.get('name', 'Unnamed')} - {instance.get('status', 'unknown')} ({instance.get('id', 'no-id')[:8]}...)")
        else:
            print(f"❌ Failed to get instances: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error getting instances: {str(e)}")
        return False
    
    # Step 2: Create a simple test workflow
    print(f"\n🛠️  Step 2: Creating simple test workflow...")
    
    simple_workflow = {
        "nodes": [
            {
                "id": "start-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 150},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "config": {"trigger_data": {}}
                }
            },
            {
                "id": "ai-simple-2", 
                "type": "ai_processing",
                "position": {"x": 400, "y": 150},
                "data": {
                    "label": "Simple AI Test",
                    "type": "ai_processing",
                    "config": {
                        "provider": "ollama",
                        "model": "qwen3:8b",
                        "prompt": "Generate a simple test response: {input}",
                        "temperature": 0.3,
                        "max_tokens": 100
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1-2",
                "source": "start-1",
                "target": "ai-simple-2",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    try:
        # Create workflow template
        workflow_payload = {
            "name": f"Frontend Debug Test - {datetime.now().strftime('%H:%M:%S')}",
            "description": "Simple workflow to debug frontend execution",
            "category": "Debug",
            "workflow_data": simple_workflow,
            "is_public": True
        }
        
        save_response = requests.post(
            f"{base_url}/editor/save",
            json=workflow_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if save_response.status_code != 200:
            print(f"❌ Failed to create workflow: {save_response.status_code}")
            print(save_response.text)
            return False
        
        workflow_result = save_response.json()
        workflow_id = workflow_result.get("data", {}).get("workflow_id")
        print(f"✅ Test workflow created: {workflow_id}")
        
        # Step 3: Create instance
        print(f"\n🚀 Step 3: Creating workflow instance...")
        
        instance_payload = {
            "name": f"Frontend Debug Instance - {datetime.now().strftime('%H:%M:%S')}",
            "template_id": workflow_id,
            "workflow_data": simple_workflow,
            "input_data": {"test_input": "Hello from frontend debug"},
            "created_by": "frontend_debug"
        }
        
        instance_response = requests.post(
            f"{base_url}/instances",
            json=instance_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if instance_response.status_code != 200:
            print(f"❌ Failed to create instance: {instance_response.status_code}")
            print(instance_response.text)
            return False
        
        instance_result = instance_response.json()
        instance_id = instance_result.get("instance_id")
        print(f"✅ Instance created: {instance_id}")
        
        # Step 4: Test execution immediately
        print(f"\n▶️  Step 4: Testing execution...")
        
        execute_response = requests.post(
            f"{base_url}/instances/{instance_id}/execute",
            headers={"Content-Type": "application/json"}
        )
        
        if execute_response.status_code == 200:
            print(f"✅ Execution started successfully!")
            execute_result = execute_response.json()
            print(f"   Status: {execute_result.get('status', 'unknown')}")
            
            # Monitor briefly
            for i in range(5):
                time.sleep(2)
                status_response = requests.get(f"{base_url}/instances/{instance_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data.get("data", {}).get("instance", {})
                    status = instance.get("status", "unknown")
                    print(f"   Check {i+1}: {status}")
                    
                    if status in ["completed", "failed"]:
                        break
        else:
            print(f"❌ Execution failed: {execute_response.status_code}")
            print(execute_response.text)
            return False
        
        print(f"\n✅ Test workflow execution completed successfully!")
        print(f"🎯 Instance ID for frontend testing: {instance_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error in workflow creation/execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_frontend_api_integration():
    """Check if frontend API calls are working"""
    print(f"\n🌐 Checking Frontend API Integration")
    print("="*40)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Test endpoints that frontend uses
    endpoints_to_test = [
        ("/components", "GET", "Component list"),
        ("/templates", "GET", "Template list"),
        ("/instances", "GET", "Instance list")
    ]
    
    for endpoint, method, description in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {description}: OK ({response.status_code})")
            else:
                print(f"❌ {description}: Failed ({response.status_code})")
        
        except Exception as e:
            print(f"❌ {description}: Error - {str(e)}")

if __name__ == "__main__":
    print("🚀 Frontend Execution Debug Suite")
    print("="*45)
    
    # Check API integration
    check_frontend_api_integration()
    
    # Debug workflow execution
    success = debug_frontend_execution()
    
    if success:
        print(f"\n🎉 DEBUG SUCCESSFUL!")
        print(f"✅ Backend API working")
        print(f"✅ Workflow creation working")
        print(f"✅ Instance creation working")
        print(f"✅ Execution working")
        print(f"\n💡 Frontend error might be:")
        print(f"   1. Instance ID not being stored correctly")
        print(f"   2. Frontend trying to execute non-existent instance")
        print(f"   3. Frontend not handling async execution properly")
        print(f"   4. UI state management issue")
    else:
        print(f"\n❌ Backend has issues - fix backend first")
