#!/usr/bin/env python3
"""
Create and run new workflow to test auto-add Prompt column
"""

import requests
import json
import time

def create_and_test_new_workflow():
    """Create new workflow instance and test auto-add Prompt"""
    print("🚀 CREATING NEW WORKFLOW TO TEST AUTO-ADD PROMPT")
    print("="*55)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Create a workflow instance that specifically targets TEST_NEW worksheet
    # We'll use the existing template but create new instance
    
    template_id = "1643d9b9-82a7-4fe0-a56d-11f96a922d0f"  # AI -> Sheets Test
    
    try:
        # Get template details first
        template_response = requests.get(f"{base_url}/workflow/templates/{template_id}")
        
        if template_response.status_code == 200:
            print("✅ Found existing template")
            
            # Create instance using backend API directly
            instance_data = {
                "template_id": template_id,
                "name": "Auto Prompt Test - " + 
                       __import__('datetime').datetime.now().strftime("%H:%M:%S"),
                "description": "Test auto-add Prompt column to TEST_NEW worksheet"
            }
            
            print("📤 Creating new instance...")
            
            instance_response = requests.post(
                f"{base_url}/workflow/instances",
                json=instance_data
            )
            
            print(f"📥 Instance creation response: {instance_response.status_code}")
            
            if instance_response.status_code == 201:
                instance_resp_data = instance_response.json()
                instance_id = instance_resp_data["data"]["id"]
                print(f"✅ Created instance: {instance_id}")
                
                # Execute the workflow
                print("🚀 Executing workflow...")
                
                execute_response = requests.post(
                    f"{base_url}/workflow/instances/{instance_id}/execute"
                )
                
                if execute_response.status_code == 200:
                    print("✅ Workflow execution started")
                    
                    # Monitor execution
                    max_wait = 25
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
                                print("🎉 Workflow completed!")
                                
                                # Analyze results
                                return analyze_workflow_results(base_url, instance_id)
                                
                            elif status == "failed":
                                print("❌ Workflow failed")
                                return analyze_workflow_results(base_url, instance_id)
                        
                        time.sleep(2)
                        wait_time += 2
                    
                    print("⏰ Timeout waiting for completion")
                    return analyze_workflow_results(base_url, instance_id)
                
                else:
                    print(f"❌ Failed to execute: {execute_response.status_code}")
                    print(f"Response: {execute_response.text}")
                    return False
            
            else:
                print(f"❌ Failed to create instance: {instance_response.status_code}")
                print(f"Response: {instance_response.text}")
                return False
        
        else:
            print(f"❌ Failed to get template: {template_response.status_code}")
            return False
    
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def analyze_workflow_results(base_url, instance_id):
    """Analyze workflow execution results"""
    print(f"\n🔍 ANALYZING WORKFLOW RESULTS")
    print("="*35)
    
    try:
        logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
        
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            steps = logs_data.get("data", {}).get("steps", [])
            
            for step in steps:
                if step['step_type'] == 'google_sheets_write':
                    print(f"📝 GOOGLE SHEETS WRITE STEP:")
                    
                    # Input analysis
                    input_data = step.get('input_data', {})
                    worksheet_name = input_data.get('worksheet_name', 'NOT SET')
                    
                    print(f"   📄 Target worksheet: {worksheet_name}")
                    
                    # Output analysis
                    output = step.get('output_data', {})
                    operation = output.get('operation')
                    status = output.get('status')
                    
                    print(f"   📊 Operation: {operation}")
                    print(f"   📊 Status: {status}")
                    
                    # Data written
                    if 'data_written' in output:
                        data_written = output['data_written']
                        print(f"   📊 Rows: {data_written.get('rows_count', 0)}")
                        print(f"   📊 Columns: {data_written.get('columns_count', 0)}")
                        print(f"   📍 Range: {data_written.get('range_written', 'N/A')}")
                    
                    # Check logs for auto-add features
                    print(f"\n   📋 AUTO-ADD PROMPT LOGS:")
                    if step.get('logs'):
                        found_auto_logs = False
                        for log in step['logs']:
                            if any(keyword in log for keyword in [
                                'Adding Prompt column', 'Added Prompt column', 
                                'existing headers', 'new data headers',
                                'Aligning data', 'Auto-add', 'Prompt column'
                            ]):
                                print(f"      🎯 {log}")
                                found_auto_logs = True
                        
                        if not found_auto_logs:
                            print(f"      ❌ No auto-add Prompt logs found")
                    
                    return True
                
                elif step['step_type'] == 'ai_processing':
                    # Check AI output format
                    if step.get('output_data') and 'results_for_sheets' in step['output_data']:
                        results = step['output_data']['results_for_sheets']
                        print(f"\n🤖 AI PROCESSING OUTPUT:")
                        print(f"   📊 Results rows: {len(results)}")
                        
                        if len(results) > 0:
                            headers = results[0] if isinstance(results[0], list) else "Not list"
                            print(f"   📊 Headers: {headers}")
                            
                            if isinstance(headers, list) and "Prompt" in headers:
                                print(f"   🎯 Prompt column included in AI output ✅")
                            else:
                                print(f"   ❌ No Prompt column in AI output")
        
        return True
        
    except Exception as e:
        print(f"💥 Error analyzing results: {e}")
        return False

if __name__ == "__main__":
    success = create_and_test_new_workflow()
    
    if success:
        print(f"\n✅ Test completed successfully")
    else:
        print(f"\n❌ Test failed")
    
    print(f"\n💡 NEXT: Check worksheets to see if Prompt column was added!")
