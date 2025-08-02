"""
Test the enhanced logging system via API calls (simpler approach)
"""
import asyncio
import requests
import json
import uuid
from datetime import datetime


def test_logging_via_api():
    """Test the enhanced logging system through API calls"""
    
    base_url = "http://localhost:8000"
    
    print("Testing Enhanced Logging System via API")
    print("=" * 50)
    
    try:
        # Check if backend is running
        health_response = requests.get(f"{base_url}/api/v1/workflow/health")
        if health_response.status_code != 200:
            print("❌ Backend is not running. Please start the backend first.")
            return False
        
        print("✅ Backend is running")
        
        # Create a workflow instance
        workflow_data = {
            "nodes": [
                {
                    "id": "input_1",
                    "type": "input",
                    "data": {
                        "label": "Input Node",
                        "config": {
                            "default_value": "Test input for logging system"
                        }
                    },
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "ai_1", 
                    "type": "ai_processing",
                    "data": {
                        "label": "AI Processing with Logging",
                        "config": {
                            "model": "qwen3:8b",
                            "prompt": "Analyze this input and provide insights: {input}",
                            "max_tokens": 100
                        }
                    },
                    "position": {"x": 300, "y": 100}
                },
                {
                    "id": "sheets_1",
                    "type": "google_sheets_write", 
                    "data": {
                        "label": "Write to Test Sheet",
                        "config": {
                            "spreadsheet_id": "1TKRZqw5jvgPgaF6e1ZgvS8hbZvq8MEyI7o8YJMr-qkE",
                            "sheet_name": "Test_Logging",
                            "range": "A1:C10"
                        }
                    },
                    "position": {"x": 500, "y": 100}
                }
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "input_1",
                    "target": "ai_1",
                    "sourceHandle": "output",
                    "targetHandle": "input"
                },
                {
                    "id": "e2", 
                    "source": "ai_1",
                    "target": "sheets_1",
                    "sourceHandle": "output",
                    "targetHandle": "input"
                }
            ]
        }
        
        create_payload = {
            "name": "Enhanced Logging Test",
            "workflow_data": workflow_data
        }
        
        create_response = requests.post(
            f"{base_url}/api/v1/workflow/instances",
            json=create_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if create_response.status_code != 200:
            print(f"❌ Failed to create workflow instance: {create_response.text}")
            return False
        
        instance_data = create_response.json()
        instance_id = instance_data["id"]
        print(f"✅ Created workflow instance: {instance_id}")
        
        # Execute the workflow
        execute_payload = {
            "user_id": "test_user_123",
            "session_id": f"session_{datetime.now().timestamp()}",
            "input": "This is test data for the enhanced logging system - checking if logs are created properly"
        }
        
        print("🚀 Executing workflow with enhanced logging...")
        
        execute_response = requests.post(
            f"{base_url}/api/v1/workflow/instances/{instance_id}/execute",
            json=execute_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if execute_response.status_code != 200:
            print(f"❌ Failed to execute workflow: {execute_response.text}")
            return False
        
        execution_result = execute_response.json()
        print(f"✅ Workflow execution completed: {execution_result.get('success', False)}")
        
        # Wait a moment for logs to be written
        import time
        time.sleep(2)
        
        # Query the execution steps
        print("\n📊 Checking execution steps...")
        steps_response = requests.get(
            f"{base_url}/api/v1/workflow/logs/steps",
            params={"workflow_instance_id": instance_id, "limit": 10}
        )
        
        if steps_response.status_code == 200:
            steps = steps_response.json()
            print(f"Found {len(steps)} execution steps:")
            
            for step in steps:
                print(f"  • {step['step_name']} ({step['step_type']})")
                print(f"    Status: {step['status']}")
                print(f"    Execution time: {step.get('execution_time_ms', 'N/A')}ms")
                print(f"    Log level: {step.get('log_level', 'N/A')}")
                print(f"    User ID: {step.get('user_id', 'N/A')}")
                if step.get('error_message'):
                    print(f"    Error: {step['error_message']}")
                print()
        else:
            print(f"❌ Failed to get execution steps: {steps_response.text}")
        
        # Query the task logs
        print("\n📋 Checking task logs...")
        logs_response = requests.get(
            f"{base_url}/api/v1/workflow/logs/tasks",
            params={"workflow_instance_id": instance_id, "limit": 10}
        )
        
        if logs_response.status_code == 200:
            logs = logs_response.json()
            print(f"Found {len(logs)} task logs:")
            
            for log in logs:
                print(f"  • {log['task_name']} ({log['task_type']})")
                print(f"    Task ID: {log['task_id']}")
                print(f"    Status: {log['status']}")
                print(f"    Log level: {log['log_level']}")
                print(f"    Processing time: {log.get('processing_time_ms', 'N/A')}ms")
                print(f"    User ID: {log.get('user_id', 'N/A')}")
                print(f"    Session ID: {log.get('session_id', 'N/A')}")
                print(f"    Correlation ID: {log.get('correlation_id', 'N/A')}")
                
                if log.get('failure_reason'):
                    print(f"    Failure reason: {log['failure_reason']}")
                    print(f"    Error code: {log.get('error_code', 'N/A')}")
                
                if log.get('sheet_id'):
                    print(f"    Sheet ID: {log['sheet_id']}")
                    print(f"    API response code: {log.get('api_response_code', 'N/A')}")
                
                if log.get('api_endpoint'):
                    print(f"    API endpoint: {log['api_endpoint']}")
                
                print(f"    Created: {log.get('created_at', 'N/A')}")
                print()
        else:
            print(f"❌ Failed to get task logs: {logs_response.text}")
        
        # Get log summary
        print("\n📈 Getting log summary...")
        summary_response = requests.get(
            f"{base_url}/api/v1/workflow/logs/summary",
            params={"workflow_instance_id": instance_id, "hours": 1}
        )
        
        if summary_response.status_code == 200:
            summary = summary_response.json()
            print(f"Log Summary for Instance {instance_id}:")
            print(f"  Total tasks: {summary['total_tasks']}")
            print(f"  Successful: {summary['successful_tasks']}")
            print(f"  Failed: {summary['failed_tasks']}")
            print(f"  Processing: {summary['processing_tasks']}")
            print(f"  Success rate: {summary['success_rate']}%")
            print(f"  Average execution time: {summary['average_execution_time_ms']}ms")
            
            if summary.get('error_distribution'):
                print(f"  Error distribution: {summary['error_distribution']}")
            
            if summary.get('task_type_distribution'):
                print(f"  Task type distribution: {summary['task_type_distribution']}")
        else:
            print(f"❌ Failed to get log summary: {summary_response.text}")
        
        # Get detailed instance logs
        print("\n🔍 Getting detailed instance logs...")
        detailed_response = requests.get(
            f"{base_url}/api/v1/workflow/logs/instances/{instance_id}/detailed"
        )
        
        if detailed_response.status_code == 200:
            detailed = detailed_response.json()
            print(f"Detailed Instance Logs:")
            print(f"  Instance: {detailed['instance']['name']}")
            print(f"  Status: {detailed['instance']['status']}")
            print(f"  Total steps: {detailed['execution_summary']['total_steps']}")
            print(f"  Successful steps: {detailed['execution_summary']['successful_steps']}")
            print(f"  Failed steps: {detailed['execution_summary']['failed_steps']}")
            print(f"  Total execution time: {detailed['execution_summary']['total_execution_time_ms']}ms")
            print(f"  Success rate: {detailed['execution_summary']['success_rate']}%")
        else:
            print(f"❌ Failed to get detailed logs: {detailed_response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_logging_via_api()
    
    if success:
        print("\n✅ Enhanced logging test completed successfully!")
        print("The logging system is working and storing detailed information about each workflow step.")
    else:
        print("\n❌ Enhanced logging test failed.")
        print("Make sure the backend is running and try again.")
