#!/usr/bin/env python3
"""
Manual Test Workflow with Specific Worksheet
"""

import requests
import json
import time

def test_workflow_with_worksheet():
    """Test running existing workflow and monitor results"""
    print("🔍 TESTING WORKFLOW WITH SPECIFIC WORKSHEET")
    print("="*50)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Check recent instances to see what's happening
    try:
        instances_response = requests.get(f"{base_url}/workflow/instances?limit=3")
        
        if instances_response.status_code == 200:
            instances_data = instances_response.json()
            instances = instances_data.get("data", {}).get("instances", [])
            
            print(f"📊 Recent instances:")
            
            for instance in instances:
                instance_id = instance["id"]
                instance_name = instance["name"]
                status = instance["status"]
                created_at = instance["created_at"]
                
                print(f"\n🔸 {instance_name}")
                print(f"   ID: {instance_id[:8]}...")
                print(f"   Status: {status}")
                print(f"   Created: {created_at}")
                
                if status == "completed":
                    # Get detailed logs
                    logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                    
                    if logs_response.status_code == 200:
                        logs_data = logs_response.json()
                        steps = logs_data.get("data", {}).get("steps", [])
                        
                        for step in steps:
                            if step['step_type'] == 'google_sheets_write':
                                output = step.get('output_data', {})
                                operation = output.get('operation')
                                status = output.get('status')
                                
                                print(f"   📝 Sheets Write: {operation} -> {status}")
                                
                                if 'data_written' in output:
                                    data_written = output['data_written']
                                    rows_count = data_written.get('rows_count', 0)
                                    range_written = data_written.get('range_written', 'N/A')
                                    print(f"      ✅ Wrote {rows_count} rows to {range_written}")
                                
                                # Check what worksheet it wrote to
                                input_data = step.get('input_data', {})
                                worksheet_name = input_data.get('worksheet_name', 'NOT SET')
                                print(f"      📄 Target worksheet: {worksheet_name}")
                                
                                if worksheet_name == "NOT SET":
                                    print(f"      ⚠️  Using default worksheet (TEST121)")
                                elif worksheet_name == "TEST_NEW":
                                    print(f"      🎯 Correctly targeting TEST_NEW!")
                            
                            elif step['step_type'] == 'ai_processing':
                                if step.get('output_data') and 'results_for_sheets' in step['output_data']:
                                    results = step['output_data']['results_for_sheets']
                                    print(f"   🤖 AI Results: {len(results)} rows")
                                    
                                    if len(results) > 0:
                                        headers = results[0] if isinstance(results[0], list) else "Not list"
                                        if isinstance(headers, list) and "Prompt" in headers:
                                            print(f"      🎯 Prompt column included!")
                                        else:
                                            print(f"      ❌ No Prompt column")
        
        else:
            print(f"❌ Failed to get instances: {instances_response.status_code}")
    
    except Exception as e:
        print(f"💥 Error: {e}")

def check_test_new_worksheet():
    """Check current state of TEST_NEW worksheet"""
    print("\n🔍 CHECKING TEST_NEW WORKSHEET")
    print("="*35)
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        import os
        
        # Set up credentials
        credentials_path = os.path.join("backend", "credentials.json")
        
        if not os.path.exists(credentials_path):
            print(f"❌ Credentials not found: {credentials_path}")
            return
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet = client.open_by_key(sheet_id)
        
        # Get TEST_NEW worksheet
        worksheet = sheet.worksheet("TEST_NEW")
        
        # Get all data
        values = worksheet.get_all_values()
        data_rows = len([row for row in values if any(cell.strip() for cell in row)])
        
        print(f"📄 TEST_NEW worksheet:")
        print(f"   Total rows with data: {data_rows}")
        
        if len(values) > 0:
            headers = values[0]
            print(f"   Headers: {headers}")
            
            if "Prompt" in headers:
                prompt_col_index = headers.index("Prompt")
                print(f"   🎯 Prompt column at index {prompt_col_index}")
                
                # Check for data in Prompt column
                prompt_data = []
                for i, row in enumerate(values[1:], 1):
                    if len(row) > prompt_col_index and row[prompt_col_index].strip():
                        prompt_data.append((i, row[prompt_col_index]))
                
                print(f"   💬 Rows with Prompt data: {len(prompt_data)}")
                
                if prompt_data:
                    print(f"   📝 Recent prompts:")
                    for row_num, prompt in prompt_data[-3:]:  # Show last 3
                        print(f"      Row {row_num}: {prompt[:100]}...")
                else:
                    print(f"   ❌ No data in Prompt column")
            else:
                print(f"   ❌ No Prompt column found")
    
    except Exception as e:
        print(f"💥 Error checking worksheet: {e}")

if __name__ == "__main__":
    test_workflow_with_worksheet()
    check_test_new_worksheet()
