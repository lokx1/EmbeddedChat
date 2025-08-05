#!/usr/bin/env python3
"""
Test workflow with corrected AI extraction logic and Ollama
"""

import requests
import json
import time

def test_corrected_workflow():
    print("🔧 Testing workflow with corrected AI extraction logic...")
    
    # Load corrected workflow config
    with open('d:/EmbeddedChat/workflow_config_test_new.json', 'r', encoding='utf-8') as f:
        workflow_config = json.load(f)
    
    print(f"📋 Workflow: {workflow_config['name']}")
    print(f"📋 Using provider: {workflow_config['components'][2]['config']['configuration']['provider']}")
    print(f"📋 Using model: {workflow_config['components'][2]['config']['configuration']['model']}")
    
    # Wait for backend to be ready
    print("⏳ Waiting for backend to be ready...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                break
        except:
            pass
        print(f"   Waiting... ({i+1}/10)")
        time.sleep(2)
    else:
        print("❌ Backend not ready, but continuing anyway...")
    
    try:
        print("\n📤 Creating workflow instance...")
        
        # Step 1: Create workflow instance
        create_response = requests.post(
            "http://localhost:8000/api/v1/workflow/instances",
            json={
                "name": "Test Corrected AI Extraction",
                "workflow_data": workflow_config,
                "input_data": {},
                "created_by": "test_user"
            },
            timeout=30
        )
        
        print(f"📥 Create response status: {create_response.status_code}")
        
        if create_response.status_code != 200:
            print(f"❌ Failed to create instance: {create_response.text}")
            return
        
        create_result = create_response.json()
        instance_id = create_result.get("instance_id")
        print(f"✅ Created instance: {instance_id}")
        
        # Step 2: Execute workflow instance
        print(f"\n🚀 Executing workflow instance...")
        execute_response = requests.post(
            f"http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute",
            json={},
            timeout=120
        )
        
        print(f"📥 Execute response status: {execute_response.status_code}")
        
        if execute_response.status_code == 200:
            result = execute_response.json()
            print(f"✅ Workflow execution started!")
            print(f"📊 Status: {result.get('status')}")
            
            # Wait a bit for execution to complete
            print("⏳ Waiting for execution to complete...")
            time.sleep(10)
            
            # Check execution status
            status_response = requests.get(
                f"http://localhost:8000/api/v1/workflow/instances/{instance_id}",
                timeout=30
            )
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                print(f"� Final status: {status_result.get('status')}")
                
                # Try to get execution results
                if status_result.get('status') == 'completed':
                    print("🎯 Execution completed! Check your Google Sheet for updated Prompt column!")
                else:
                    print("⚠️ Execution may still be running or failed. Check backend logs.")
        
        elif execute_response.status_code == 404:
            print("❌ Execute endpoint not found - check if backend routes are correct")
        else:
            print(f"❌ Execute error {execute_response.status_code}: {execute_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - make sure it's running on port 8000")
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    test_corrected_workflow()
