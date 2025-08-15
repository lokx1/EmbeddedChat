#!/usr/bin/env python3
"""
Debug the data flow between AI Processing and Google Sheets Write
"""

import requests
import json

def debug_data_flow():
    """Debug the latest workflow execution to see data flow"""
    
    # Get the most recent instance
    response = requests.get('http://localhost:8000/api/v1/workflow/instances')
    if response.status_code == 200:
        instances = response.json()['data']['instances']
        if instances:
            latest = instances[0]  # Most recent
            instance_id = latest['id']
            print(f"🔍 Debugging instance: {instance_id}")
            print(f"📝 Name: {latest['name']}")
            print(f"📊 Status: {latest['status']}")
            
            # Get detailed execution logs
            logs_response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs')
            if logs_response.status_code == 200:
                logs_data = logs_response.json()['data']
                steps = logs_data.get('steps', [])
                
                print(f"\\n📝 Step-by-step data flow:")
                
                for step in steps:
                    print(f"\\n🔹 {step['step_type']} ({step['node_id']}):")
                    print(f"   Status: {step['status']}")
                    print(f"   Time: {step['created_at']}")
                    
                    if step.get('input_data'):
                        input_keys = list(step['input_data'].keys()) if isinstance(step['input_data'], dict) else 'non-dict'
                        print(f"   📥 Input keys: {input_keys}")
                        
                    if step.get('output_data'):
                        output_keys = list(step['output_data'].keys()) if isinstance(step['output_data'], dict) else 'non-dict'
                        print(f"   📤 Output keys: {output_keys}")
                        
                        # Show specific data for important steps
                        if step['step_type'] == 'google_sheets':
                            if 'records' in step['output_data']:
                                records_count = len(step['output_data']['records'])
                                print(f"   📊 Records read: {records_count}")
                        
                        if step['step_type'] == 'ai_processing':
                            if 'response' in step['output_data']:
                                response_preview = str(step['output_data']['response'])[:100] + "..."
                                print(f"   🤖 AI Response: {response_preview}")
                                
                        if step['step_type'] == 'google_sheets_write':
                            print(f"   💾 Write attempt details:")
                            print(f"       Available input keys: {step.get('input_data', {}).keys()}")
                    
                    if step.get('error_message'):
                        print(f"   ❌ Error: {step['error_message']}")
                        
                print(f"\\n🔍 Data Flow Analysis:")
                
                # Analyze what data each step produced
                google_sheets_output = None
                ai_output = None
                write_input = None
                
                for step in steps:
                    if step['step_type'] == 'google_sheets' and step.get('output_data'):
                        google_sheets_output = step['output_data']
                        
                    elif step['step_type'] == 'ai_processing' and step.get('output_data'):
                        ai_output = step['output_data']
                        
                    elif step['step_type'] == 'google_sheets_write':
                        write_input = step.get('input_data', {})
                
                if google_sheets_output:
                    print(f"✅ Google Sheets Read produced data")
                    if 'records' in google_sheets_output:
                        print(f"   - {len(google_sheets_output['records'])} records")
                    
                if ai_output:
                    print(f"✅ AI Processing produced data")
                    if 'response' in ai_output:
                        print(f"   - AI response available")
                    
                if write_input:
                    print(f"📥 Google Sheets Write received:")
                    for key, value in write_input.items():
                        if key == 'data' and isinstance(value, list):
                            print(f"   - {key}: list with {len(value)} items")
                        elif isinstance(value, str) and len(value) > 50:
                            print(f"   - {key}: '{value[:50]}...'")
                        else:
                            print(f"   - {key}: {value}")
                else:
                    print(f"❌ Google Sheets Write received no input data")
                    
                return True
            else:
                print(f"❌ Failed to get logs: {logs_response.text}")
                return False
        else:
            print("No workflow instances found")
            return False
    else:
        print(f"❌ Failed to get instances: {response.text}")
        return False

if __name__ == "__main__":
    print("=== Data Flow Debug ===\\n")
    debug_data_flow()
