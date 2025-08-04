#!/usr/bin/env python3
"""
Check Google Sheets Write Configuration and Results
"""

import requests
import json

def check_sheets_config():
    """Check what sheet the workflow is writing to"""
    print("🔍 CHECKING GOOGLE SHEETS WRITE CONFIGURATION")
    print("="*60)
    
    base_url = "http://localhost:8000/api/v1"
    
    try:
        # Get the most recent completed instance
        instances_response = requests.get(f"{base_url}/workflow/instances?limit=1")
        
        if instances_response.status_code == 200:
            instances_data = instances_response.json()
            instances = instances_data.get("data", {}).get("instances", [])
            
            if instances:
                instance = instances[0]
                instance_id = instance["id"]
                instance_name = instance["name"]
                
                print(f"📊 Latest Instance: {instance_name}")
                print(f"🆔 ID: {instance_id}")
                
                # Get detailed logs
                logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                if logs_response.status_code == 200:
                    logs_data = logs_response.json()
                    steps = logs_data.get("data", {}).get("steps", [])
                    
                    for step in steps:
                        if step['step_type'] == 'google_sheets_write':
                            print(f"\n📝 GOOGLE SHEETS WRITE STEP")
                            print(f"   Status: {step['status']}")
                            
                            # Check input data (configuration)
                            if step.get('input_data'):
                                input_data = step['input_data']
                                sheet_id = input_data.get('sheet_id', 'NOT SET')
                                worksheet_name = input_data.get('worksheet_name', 'NOT SET')
                                
                                print(f"   📋 Target Sheet ID: {sheet_id}")
                                print(f"   📄 Target Worksheet: {worksheet_name}")
                                
                                if 'data' in input_data:
                                    data_rows = len(input_data['data'])
                                    print(f"   📊 Data to write: {data_rows} rows")
                                    
                                    # Show headers if available
                                    if data_rows > 0:
                                        headers = input_data['data'][0]
                                        print(f"   📋 Headers: {headers}")
                            
                            # Check output data (results)
                            if step.get('output_data'):
                                output = step['output_data']
                                print(f"\n   ✅ OUTPUT RESULTS:")
                                print(f"      Operation: {output.get('operation')}")
                                print(f"      Status: {output.get('status')}")
                                
                                if 'data_written' in output:
                                    data_written = output['data_written']
                                    print(f"      Rows written: {data_written.get('rows_count', 0)}")
                                    print(f"      Range written: {data_written.get('range_written', 'N/A')}")
                                    
                                    # Show actual sheet URL if available
                                    if 'sheet_url' in data_written:
                                        print(f"      📍 Sheet URL: {data_written['sheet_url']}")
                            
                            # Check logs for any specific messages
                            if step.get('logs'):
                                print(f"\n   📋 RELEVANT LOGS:")
                                for log in step['logs']:
                                    if any(keyword in log for keyword in ['Writing', 'Wrote', 'sheet', 'worksheet', 'range']):
                                        print(f"      {log}")
                        
                        elif step['step_type'] == 'google_sheets' and step['status'] == 'completed':
                            # This is the input step - show what sheet we're reading from
                            if step.get('input_data'):
                                input_data = step['input_data']
                                source_sheet = input_data.get('sheet_id', 'NOT SET')
                                source_worksheet = input_data.get('worksheet_name', 'NOT SET')
                                
                                print(f"\n📖 GOOGLE SHEETS READ STEP")
                                print(f"   📋 Source Sheet ID: {source_sheet}")
                                print(f"   📄 Source Worksheet: {source_worksheet}")
                                
                            if step.get('output_data'):
                                output = step['output_data']
                                if 'data' in output:
                                    rows_read = len(output['data'])
                                    print(f"   📊 Rows read: {rows_read}")
                
        else:
            print(f"❌ Failed to get instances: {instances_response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    check_sheets_config()
