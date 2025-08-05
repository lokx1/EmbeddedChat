#!/usr/bin/env python3
"""
Quick Debug AI to Sheets Flow
"""

import requests
import json
import time

def quick_debug():
    """Quick debug of workflow execution"""
    print("🔍 QUICK DEBUG - AI TO SHEETS FLOW")
    print("="*50)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Simple test - just check existing workflow instance
    # Get recent instances
    try:
        instances_response = requests.get(f"{base_url}/workflow/instances?limit=5")
        
        if instances_response.status_code == 200:
            instances_data = instances_response.json()
            instances = instances_data.get("data", {}).get("instances", [])
            
            print(f"📊 Found {len(instances)} recent instances")
            
            for instance in instances[:2]:  # Check last 2 instances
                instance_id = instance["id"]
                instance_name = instance["name"]
                status = instance["status"]
                
                print(f"\n🔸 Instance: {instance_name} ({instance_id[:8]}...)")
                print(f"   Status: {status}")
                
                if status == "completed":
                    # Get logs for this instance
                    logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                    if logs_response.status_code == 200:
                        logs_data = logs_response.json()
                        steps = logs_data.get("data", {}).get("steps", [])
                        
                        for step in steps:
                            step_type = step['step_type']
                            step_status = step['status']
                            
                            print(f"      📋 {step_type}: {step_status}")
                            
                            # Check AI Processing output
                            if step_type == 'ai_processing' and step_status == 'completed':
                                if step.get('output_data') and 'results_for_sheets' in step['output_data']:
                                    sheets_data = step['output_data']['results_for_sheets']
                                    print(f"         ✅ AI created results_for_sheets: {len(sheets_data)} rows")
                                    if len(sheets_data) > 0:
                                        headers = sheets_data[0] if isinstance(sheets_data[0], list) else "Not list format"
                                        print(f"         📊 Headers: {headers}")
                                        
                                        # Check for Prompt column
                                        if isinstance(headers, list) and "Prompt" in headers:
                                            prompt_index = headers.index("Prompt")
                                            print(f"         🎯 Prompt column found at index {prompt_index}")
                                            
                                            # Show first data row
                                            if len(sheets_data) > 1:
                                                first_row = sheets_data[1]
                                                if isinstance(first_row, list) and len(first_row) > prompt_index:
                                                    prompt_value = first_row[prompt_index]
                                                    print(f"         💬 First prompt: {prompt_value[:100]}...")
                                else:
                                    print(f"         ❌ No results_for_sheets in AI output")
                            
                            # Check Google Sheets Write output
                            elif step_type == 'google_sheets_write':
                                if step.get('output_data'):
                                    output = step['output_data']
                                    operation = output.get('operation', 'N/A')
                                    status = output.get('status', 'N/A')
                                    print(f"         📝 Sheets operation: {operation}, status: {status}")
                                    
                                    if status == 'success':
                                        rows_written = output.get('data_written', {}).get('rows_count', 0)
                                        print(f"         ✅ Successfully wrote {rows_written} rows")
                                    elif status == 'simulated':
                                        print(f"         ⚠️  Still in simulation mode")
                                        
                                # Check logs for data flow issues
                                if step.get('logs'):
                                    for log in step['logs']:
                                        if "🎯 Found results_for_sheets" in log:
                                            print(f"         🎯 {log}")
                                        elif "No results_for_sheets" in log:
                                            print(f"         ❌ {log}")
                        
        else:
            print(f"❌ Failed to get instances: {instances_response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    quick_debug()
