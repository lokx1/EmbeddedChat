#!/usr/bin/env python3
"""
Test workflow via API calls to running backend
"""

import requests
import json
import time

def test_workflow_api():
    print("🚀 Testing workflow via API...")
    
    # Load the workflow configuration
    with open('workflow_config_test_new.json', 'r', encoding='utf-8') as f:
        workflow_config = json.load(f)
    
    print(f"📋 Workflow: {workflow_config['name']}")
    print(f"📋 Components: {len(workflow_config['components'])}")
    
    # Create workflow via API
    api_base = "http://localhost:8000/api"
    
    # 1. Create workflow
    create_data = {
        "name": "Test Prompt Column Fix",
        "description": "Testing AI response in Prompt column after fix",
        "config": workflow_config
    }
    
    print("\n📡 Creating workflow...")
    try:
        response = requests.post(f"{api_base}/workflows", json=create_data)
        if response.status_code == 200:
            workflow_data = response.json()
            workflow_id = workflow_data["id"]
            print(f"✅ Workflow created with ID: {workflow_id}")
        else:
            print(f"❌ Failed to create workflow: {response.status_code} {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return
    
    # 2. Execute workflow
    print(f"\n🔄 Executing workflow {workflow_id}...")
    try:
        response = requests.post(f"{api_base}/workflows/{workflow_id}/execute")
        if response.status_code == 200:
            execution_data = response.json()
            execution_id = execution_data["execution_id"]
            print(f"✅ Execution started with ID: {execution_id}")
        else:
            print(f"❌ Failed to execute workflow: {response.status_code} {response.text}")
            return
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")
        return
    
    # 3. Monitor execution
    print(f"\n⏳ Monitoring execution...")
    max_wait = 120  # 2 minutes
    waited = 0
    
    while waited < max_wait:
        try:
            response = requests.get(f"{api_base}/workflows/executions/{execution_id}")
            if response.status_code == 200:
                execution = response.json()
                status = execution["status"]
                print(f"📊 Status: {status}")
                
                if status in ["completed", "failed"]:
                    print(f"\n✅ Execution finished!")
                    print(f"📊 Final Status: {status}")
                    print(f"⏱️ Duration: {execution.get('execution_time_ms', 0)}ms")
                    
                    if execution.get("error"):
                        print(f"❌ Error: {execution['error']}")
                    
                    # Check step results for Prompt column content
                    if "step_results" in execution:
                        for i, step in enumerate(execution["step_results"]):
                            print(f"\n📝 Step {i+1}: {step.get('step_name', 'Unknown')}")
                            print(f"   ✅ Success: {step.get('success', False)}")
                            
                            if step.get("error"):
                                print(f"   ❌ Error: {step['error']}")
                            
                            # Check AI Processing step
                            if "AI Processing" in step.get("step_name", "") and step.get("output_data"):
                                output_data = step["output_data"]
                                if "results_for_sheets" in output_data:
                                    results = output_data["results_for_sheets"]
                                    print(f"   📊 results_for_sheets: {len(results)} rows")
                                    if len(results) > 0:
                                        headers = results[0]
                                        print(f"   📊 Headers: {headers}")
                                        if len(results) > 1 and "Prompt" in headers:
                                            prompt_index = headers.index("Prompt")
                                            first_row = results[1]
                                            if len(first_row) > prompt_index:
                                                prompt_content = first_row[prompt_index]
                                                print(f"   🎯 Prompt content: '{prompt_content[:100]}...' (length: {len(prompt_content)})")
                                                if prompt_content and len(prompt_content) > 10:
                                                    print(f"   ✅ SUCCESS: Prompt column has content!")
                                                else:
                                                    print(f"   ❌ FAIL: Prompt column is empty")
                    
                    print(f"\n🎯 Check your Google Sheet now - the Prompt column should be populated!")
                    return
                
                # Wait and check again
                time.sleep(5)
                waited += 5
                
            else:
                print(f"❌ Failed to get execution status: {response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ Error monitoring execution: {e}")
            break
    
    print(f"⏰ Execution monitoring timed out after {max_wait} seconds")

if __name__ == "__main__":
    test_workflow_api()
