#!/usr/bin/env python3
"""
Check the logs of the most recent workflow execution to debug the AI response extraction
"""
import requests
import json

def check_recent_workflow_logs():
    """Check logs of the most recent workflow execution"""
    
    print("=== Checking Recent Workflow Logs ===")
    
    try:
        # Get recent instances
        instances_response = requests.get('http://localhost:8000/api/v1/workflow/instances', timeout=10)
        if instances_response.status_code != 200:
            print(f"❌ Could not fetch instances: {instances_response.status_code}")
            return
            
        instances_data = instances_response.json()
        if not instances_data.get('success'):
            print(f"❌ API error: {instances_data}")
            return
            
        instances = instances_data.get('data', {}).get('instances', [])
        print(f"📋 Found {len(instances)} instances")
        
        if not instances:
            print("❌ No workflow instances found")
            return
            
        # Get the most recent instance
        latest_instance = instances[-1]
        instance_id = latest_instance.get('id')
        instance_name = latest_instance.get('name', 'Unknown')
        
        print(f"🔍 Checking logs for instance: {instance_id} ({instance_name})")
        
        # Get detailed logs
        logs_response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs', timeout=10)
        if logs_response.status_code != 200:
            print(f"❌ Could not fetch logs: {logs_response.status_code}")
            return
            
        logs_data = logs_response.json()
        steps = logs_data.get('data', {}).get('steps', [])
        
        print(f"📋 Found {len(steps)} execution steps:")
        
        for i, step in enumerate(steps, 1):
            step_type = step.get('step_type', 'unknown')
            step_status = step.get('status', 'unknown')
            step_id = step.get('step_id', 'unknown')
            
            print(f"\n📋 Step {i}: {step_type} ({step_id})")
            print(f"   Status: {step_status}")
            
            # Show logs for this step
            step_logs = step.get('logs', [])
            if step_logs:
                print(f"   Logs ({len(step_logs)} entries):")
                for log in step_logs[-5:]:  # Show last 5 logs
                    print(f"     - {log}")
            
            # Show output data summary
            output_data = step.get('output_data', {})
            if output_data:
                print(f"   Output data keys: {list(output_data.keys())}")
                
                # Special handling for different step types
                if step_type == 'google_sheets':
                    records = output_data.get('records', [])
                    print(f"     📊 Google Sheets: {len(records)} records")
                    if records:
                        print(f"     📊 First record: {records[0]}")
                        
                elif step_type == 'ai_processing':
                    processed_results = output_data.get('processed_results', [])
                    print(f"     🤖 AI Processing: {len(processed_results)} results")
                    if processed_results:
                        first_result = processed_results[0]
                        input_data = first_result.get('input_data', {})
                        ai_response = first_result.get('ai_response', {})
                        print(f"     🤖 First result input: {list(input_data.keys())}")
                        print(f"     🤖 First result AI response type: {type(ai_response)}")
                        if isinstance(ai_response, dict):
                            print(f"     🤖 AI response keys: {list(ai_response.keys())}")
                            if 'ai_response' in ai_response:
                                ai_text = ai_response['ai_response']
                                print(f"     🤖 AI response text length: {len(ai_text) if isinstance(ai_text, str) else 'Not string'}")
                    
                    # Check if results_for_sheets exists
                    results_for_sheets = output_data.get('results_for_sheets', [])
                    if results_for_sheets:
                        print(f"     📋 Results for sheets: {len(results_for_sheets)} rows")
                        if len(results_for_sheets) > 0:
                            headers = results_for_sheets[0] if results_for_sheets else []
                            print(f"     📋 Headers: {headers}")
                            if len(results_for_sheets) > 1:
                                first_data_row = results_for_sheets[1]
                                print(f"     📋 First data row length: {len(first_data_row)}")
                                # Check prompt column (last column)
                                if first_data_row and len(first_data_row) > 0:
                                    prompt_content = first_data_row[-1]
                                    print(f"     📋 Prompt content length: {len(prompt_content) if isinstance(prompt_content, str) else 'Not string'}")
                                    if isinstance(prompt_content, str) and len(prompt_content) > 0:
                                        print(f"     📋 Prompt preview: {prompt_content[:100]}...")
                                    else:
                                        print(f"     ❌ Prompt column is empty or invalid!")
                        
                elif step_type == 'google_sheets_write':
                    data_written = output_data.get('data_written', {})
                    rows_count = data_written.get('rows_count', 0)
                    print(f"     📝 Google Sheets Write: {rows_count} rows written")
            
            # Show error if any
            error = step.get('error')
            if error:
                print(f"   ❌ Error: {error}")
                
        print(f"\n✅ Log analysis complete")
        
    except Exception as e:
        print(f"❌ Error checking logs: {e}")

if __name__ == "__main__":
    check_recent_workflow_logs()
