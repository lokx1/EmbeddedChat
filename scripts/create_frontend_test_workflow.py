#!/usr/bin/env python3
"""
Create Simple Workflow for Frontend Testing
"""

import requests
import json
from datetime import datetime

def create_simple_frontend_workflow():
    """Create a simple workflow that frontend can easily execute"""
    print("🛠️  Creating Simple Frontend Test Workflow")
    print("="*50)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Very simple workflow with just manual trigger + AI
    simple_workflow = {
        "nodes": [
            {
                "id": "start-1",
                "type": "manual_trigger",
                "position": {"x": 200, "y": 200},
                "data": {
                    "label": "Start Trigger",
                    "type": "manual_trigger",
                    "config": {
                        "trigger_data": {
                            "message": "Frontend test execution"
                        }
                    }
                }
            },
            {
                "id": "ai-test-2",
                "type": "ai_processing", 
                "position": {"x": 500, "y": 200},
                "data": {
                    "label": "AI Processing Test",
                    "type": "ai_processing",
                    "config": {
                        "provider": "ollama",
                        "model": "qwen3:8b",
                        "prompt": "Generate a simple greeting message for: {input}",
                        "temperature": 0.5,
                        "max_tokens": 50
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-start-ai",
                "source": "start-1",
                "target": "ai-test-2",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    try:
        # Create workflow template
        workflow_payload = {
            "name": "Frontend Test Workflow",
            "description": "Simple workflow for frontend testing with Ollama integration",
            "category": "Testing",
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
            return None
        
        workflow_result = save_response.json()
        workflow_id = workflow_result.get("data", {}).get("workflow_id")
        print(f"✅ Simple workflow created: {workflow_id}")
        
        # Create an instance ready for frontend
        instance_payload = {
            "name": "Frontend Ready Instance",
            "template_id": workflow_id,
            "workflow_data": simple_workflow,
            "input_data": {
                "test_message": "Hello from frontend!"
            },
            "created_by": "frontend_ready"
        }
        
        instance_response = requests.post(
            f"{base_url}/instances",
            json=instance_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if instance_response.status_code != 200:
            print(f"❌ Failed to create instance: {instance_response.status_code}")
            return None
        
        instance_result = instance_response.json()
        instance_id = instance_result.get("instance_id")
        print(f"✅ Ready instance created: {instance_id}")
        
        print(f"\n🎯 Frontend Testing Instructions:")
        print(f"="*40)
        print(f"1. Open frontend: http://localhost:3000")
        print(f"2. Go to Workflows section")
        print(f"3. Look for 'Frontend Test Workflow'")
        print(f"4. Click to edit/view")
        print(f"5. Try to execute")
        print(f"\n📋 Manual Testing URLs:")
        print(f"   Workflow: GET {base_url}/templates/{workflow_id}")
        print(f"   Instance: GET {base_url}/instances/{instance_id}")
        print(f"   Execute: POST {base_url}/instances/{instance_id}/execute")
        
        return {
            "workflow_id": workflow_id,
            "instance_id": instance_id
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_manual_execution(instance_id):
    """Test manual execution of the instance"""
    print(f"\n🧪 Testing Manual Execution")
    print("="*35)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    try:
        # Execute the instance
        execute_response = requests.post(
            f"{base_url}/instances/{instance_id}/execute",
            headers={"Content-Type": "application/json"}
        )
        
        if execute_response.status_code == 200:
            print(f"✅ Manual execution successful!")
            result = execute_response.json()
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Message: {result.get('message', 'none')}")
        else:
            print(f"❌ Manual execution failed: {execute_response.status_code}")
            print(execute_response.text)
    
    except Exception as e:
        print(f"❌ Manual execution error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Frontend Workflow Setup")
    print("="*30)
    
    result = create_simple_frontend_workflow()
    
    if result:
        # Test manual execution
        test_manual_execution(result["instance_id"])
        
        print(f"\n🎯 FRONTEND TESTING READY!")
        print(f"✅ Workflow and instance created")
        print(f"✅ Manual execution tested")
        print(f"🌐 Open http://localhost:3000 to test frontend")
    else:
        print(f"\n❌ Setup failed")
