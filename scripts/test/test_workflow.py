#!/usr/bin/env python3
"""
Test Workflow Creation and Execution
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/workflow"

def create_test_workflow():
    """Tạo một workflow test với manual trigger -> http request -> ai processing -> email"""
    
    workflow_data = {
        "name": "Complete Test Workflow",
        "description": "Test workflow với manual trigger, HTTP request, AI processing, và email sender",
        "category": "test",
        "workflow_data": {
            "nodes": [
                {
                    "id": "node-1",
                    "type": "manual_trigger",
                    "position": {"x": 100, "y": 100},
                    "data": {
                        "label": "Start Workflow",
                        "type": "manual_trigger",
                        "config": {
                            "trigger_data": {"source": "test", "timestamp": "2025-08-01"}
                        }
                    }
                },
                {
                    "id": "node-2", 
                    "type": "http_request",
                    "position": {"x": 300, "y": 100},
                    "data": {
                        "label": "Fetch Weather Data",
                        "type": "http_request",
                        "config": {
                            "url": "https://api.openweathermap.org/data/2.5/weather?q=London&appid=demo",
                            "method": "GET",
                            "headers": {"Accept": "application/json"},
                            "timeout": 30
                        }
                    }
                },
                {
                    "id": "node-3",
                    "type": "ai_processing", 
                    "position": {"x": 500, "y": 100},
                    "data": {
                        "label": "Analyze Weather",
                        "type": "ai_processing",
                        "config": {
                            "provider": "openai",
                            "model": "gpt-4o",
                            "prompt": "Analyze this weather data and provide a summary: {input}",
                            "temperature": 0.7,
                            "max_tokens": 200
                        }
                    }
                },
                {
                    "id": "node-4",
                    "type": "email_sender",
                    "position": {"x": 700, "y": 100},
                    "data": {
                        "label": "Send Report",
                        "type": "email_sender", 
                        "config": {
                            "to_email": "user@example.com",
                            "subject": "Weather Report",
                            "body": "Here's your weather analysis: {input}",
                            "from_email": "workflow@example.com"
                        }
                    }
                }
            ],
            "edges": [
                {
                    "id": "edge-1",
                    "source": "node-1",
                    "target": "node-2",
                    "sourceHandle": "output",
                    "targetHandle": "input"
                },
                {
                    "id": "edge-2", 
                    "source": "node-2",
                    "target": "node-3",
                    "sourceHandle": "success",
                    "targetHandle": "input"
                },
                {
                    "id": "edge-3",
                    "source": "node-3", 
                    "target": "node-4",
                    "sourceHandle": "output",
                    "targetHandle": "input"
                }
            ],
            "viewport": {"x": 0, "y": 0, "zoom": 1}
        },
        "is_public": False
    }
    
    print("🔄 Creating test workflow...")
    response = requests.post(f"{BASE_URL}/editor/save", json=workflow_data)
    
    if response.status_code == 200:
        result = response.json()
        # Extract workflow_id from nested response structure
        workflow_id = result.get('data', {}).get('workflow_id') if result.get('success') else result.get('workflow_id')
        print(f"✅ Workflow created successfully with ID: {workflow_id}")
        return workflow_id
    else:
        print(f"❌ Failed to create workflow: {response.status_code}")
        print(response.text)
        return None

def create_workflow_instance(workflow_id: str):
    """Tạo workflow instance từ template"""
    
    instance_data = {
        "name": f"Test Execution - {int(time.time())}",
        "template_id": workflow_id,
        "workflow_data": {},  # Will be loaded from template
        "input_data": {
            "city": "London",
            "user_email": "test@example.com"
        }
    }
    
    print("🔄 Creating workflow instance...")
    response = requests.post(f"{BASE_URL}/instances", json=instance_data)
    
    if response.status_code == 200:
        result = response.json()
        instance_id = result.get('instance_id')
        print(f"✅ Instance created successfully with ID: {instance_id}")
        return instance_id
    else:
        print(f"❌ Failed to create instance: {response.status_code}")
        print(response.text)
        return None

def execute_workflow(instance_id: str):
    """Execute workflow instance"""
    
    execution_data = {
        "trigger_data": {
            "user_id": "test_user",
            "timestamp": time.time()
        }
    }
    
    print("🚀 Starting workflow execution...")
    response = requests.post(f"{BASE_URL}/instances/{instance_id}/execute", json=execution_data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Execution started successfully")
        # Extract execution info from response
        execution_id = result.get('data', {}).get('execution_id') if result.get('success') else result.get('instance_id')
        print(f"Instance ID: {execution_id}")
        return True
    else:
        print(f"❌ Failed to start execution: {response.status_code}")
        print(response.text)
        return False

def monitor_execution(instance_id: str, max_wait: int = 60):
    """Monitor workflow execution"""
    
    print("👀 Monitoring execution...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        # Get execution status
        response = requests.get(f"{BASE_URL}/instances/{instance_id}/status")
        
        if response.status_code == 200:
            result = response.json()
            status_data = result.get('data', {}) if result.get('success') else result
            current_status = status_data.get('status')
            print(f"📊 Status: {current_status}")
            
            if current_status in ['completed', 'failed', 'cancelled']:
                print(f"🏁 Execution finished with status: {current_status}")
                
                # Get execution logs
                logs_response = requests.get(f"{BASE_URL}/instances/{instance_id}/logs")
                if logs_response.status_code == 200:
                    logs = logs_response.json()
                    print("📋 Execution Logs:")
                    logs_data = logs.get('data', {}).get('logs', []) if logs.get('success') else logs.get('logs', [])
                    for log in logs_data:
                        print(f"  • {log.get('step_name')}: {log.get('status')}")
                        if log.get('error_message'):
                            print(f"    ❌ Error: {log.get('error_message')}")
                
                return current_status
        
        time.sleep(2)
    
    print("⏰ Execution monitoring timeout")
    return 'timeout'

def main():
    """Main test function"""
    print("🧪 Starting Workflow Test Suite")
    print("=" * 50)
    
    # Test 1: List available components
    print("\n1️⃣ Testing component listing...")
    response = requests.get(f"{BASE_URL}/components")
    if response.status_code == 200:
        components = response.json()
        print(f"✅ Found {len(components)} components:")
        for comp in components:
            print(f"   • {comp['name']} ({comp['type']})")
    else:
        print(f"❌ Failed to list components: {response.status_code}")
        return
    
    # Test 2: Create workflow
    print("\n2️⃣ Testing workflow creation...")
    workflow_id = create_test_workflow()
    if not workflow_id:
        return
    
    # Test 3: Create instance
    print("\n3️⃣ Testing instance creation...")
    instance_id = create_workflow_instance(workflow_id)
    if not instance_id:
        return
    
    # Test 4: Execute workflow
    print("\n4️⃣ Testing workflow execution...")
    if execute_workflow(instance_id):
        # Test 5: Monitor execution
        print("\n5️⃣ Testing execution monitoring...")
        final_status = monitor_execution(instance_id)
        
        if final_status == 'completed':
            print("\n🎉 Workflow test completed successfully!")
        else:
            print(f"\n⚠️ Workflow finished with status: {final_status}")
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed")

if __name__ == "__main__":
    main()
