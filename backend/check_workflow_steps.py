#!/usr/bin/env python3
"""Check workflow execution steps from API"""

import requests
import json

def main():
    print("🔍 Checking Workflow Execution Steps")
    print("=" * 50)
    
    instance_id = "12bf27e5-ad8e-4939-a117-1a59fef28969"
    
    try:
        # Check instance details
        response = requests.get(f"http://localhost:8000/api/v1/workflow/instances/{instance_id}")
        if response.status_code == 200:
            instance = response.json()
            print(f"📋 Instance Details:")
            print(f"  ID: {instance.get('id', 'Unknown')}")
            print(f"  Name: {instance.get('name', 'Unknown')}")
            print(f"  Status: {instance.get('status', 'Unknown')}")
            
            # Check if there's output_data
            if 'output_data' in instance:
                print(f"  Output Data: {json.dumps(instance['output_data'], indent=2)[:500]}...")
        
        # Check execution logs
        logs_response = requests.get(f"http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs")
        if logs_response.status_code == 200:
            logs = logs_response.json()
            print(f"\n📊 Execution Logs ({len(logs)} steps):")
            
            for log in logs:
                step_name = log.get('step_name', 'Unknown')
                status = log.get('status', 'Unknown')
                
                if status == 'completed':
                    print(f"  ✅ {step_name}")
                    
                    # Check output data for AI processing
                    if 'ai_processing' in step_name.lower() or 'ai asset generation' in step_name.lower():
                        output_data = log.get('output_data', {})
                        if 'processed_results' in output_data:
                            results = output_data['processed_results']
                            print(f"    🤖 AI Results: {len(results)} items processed")
                            if results:
                                first_result = results[0]
                                print(f"    📝 Sample result keys: {list(first_result.keys())}")
                        else:
                            print(f"    📊 Output: {str(output_data)[:200]}...")
                    
                    # Check output for Google Sheets Write
                    elif 'write' in step_name.lower():
                        input_data = log.get('input_data', {})
                        output_data = log.get('output_data', {})
                        error_msg = log.get('error_message', '')
                        
                        print(f"    📝 Input config: sheet_name={input_data.get('sheet_name')}")
                        print(f"    📊 Output: {output_data}")
                        if error_msg:
                            print(f"    ❌ Error: {error_msg}")
                elif status == 'failed':
                    print(f"  ❌ {step_name}")
                    error_msg = log.get('error_message', '')
                    if error_msg:
                        print(f"    Error: {error_msg}")
                else:
                    print(f"  ⏳ {step_name} - {status}")
        else:
            print(f"❌ Failed to get logs: {logs_response.status_code}")
            print(f"Error: {logs_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
