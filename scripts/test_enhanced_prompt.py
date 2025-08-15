#!/usr/bin/env python3
"""
Simple test for auto-add Prompt column feature
"""

import requests
import json

def test_simple_workflow_with_prompt():
    """Test workflow execution with enhanced auto-prompt feature"""
    print("🚀 TESTING ENHANCED AUTO-PROMPT FEATURE")
    print("="*50)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Use existing template and create simple instance
    template_id = "1643d9b9-82a7-4fe0-a56d-11f96a922d0f"  # AI -> Sheets Test
    
    # Create instance for a worksheet WITHOUT Prompt column initially
    instance_data = {
        "name": "Enhanced Auto Prompt Test - " + 
               __import__('datetime').datetime.now().strftime("%H:%M:%S"),
        "description": "Test enhanced auto-add Prompt column feature"
    }
    
    try:
        # First, check backend is running
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code != 200:
            print("❌ Backend not running")
            return
        
        print("✅ Backend is running")
        
        # Get the latest completed instance to see current behavior
        instances_response = requests.get(f"{base_url}/workflow/instances?limit=1")
        
        if instances_response.status_code == 200:
            instances_data = instances_response.json()
            instances = instances_data.get("data", {}).get("instances", [])
            
            if instances:
                instance = instances[0]
                instance_id = instance["id"]
                instance_name = instance["name"]
                status = instance["status"]
                
                print(f"📊 Latest instance: {instance_name}")
                print(f"🆔 ID: {instance_id[:8]}...")
                print(f"📊 Status: {status}")
                
                if status == "completed":
                    # Get detailed logs to see if new auto-add feature worked
                    logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                    
                    if logs_response.status_code == 200:
                        logs_data = logs_response.json()
                        steps = logs_data.get("data", {}).get("steps", [])
                        
                        for step in steps:
                            if step['step_type'] == 'google_sheets_write':
                                print(f"\n📝 GOOGLE SHEETS WRITE ANALYSIS:")
                                
                                output = step.get('output_data', {})
                                operation = output.get('operation')
                                status = output.get('status')
                                
                                print(f"   Operation: {operation}")
                                print(f"   Status: {status}")
                                
                                if 'data_written' in output:
                                    data_written = output['data_written']
                                    rows_count = data_written.get('rows_count', 0)
                                    columns_count = data_written.get('columns_count', 0)
                                    range_written = data_written.get('range_written', 'N/A')
                                    
                                    print(f"   📊 Rows: {rows_count}")
                                    print(f"   📊 Columns: {columns_count}")
                                    print(f"   📍 Range: {range_written}")
                                
                                # Check input data
                                input_data = step.get('input_data', {})
                                worksheet_name = input_data.get('worksheet_name', 'NOT SET')
                                sheet_id = input_data.get('sheet_id', 'NOT SET')
                                
                                print(f"   📄 Target worksheet: {worksheet_name}")
                                print(f"   📋 Sheet ID: {sheet_id[:10]}..." if len(sheet_id) > 10 else sheet_id)
                                
                                # Check logs for auto-add Prompt column messages
                                if step.get('logs'):
                                    print(f"\n   📋 RELEVANT LOGS:")
                                    for log in step['logs']:
                                        if any(keyword in log for keyword in [
                                            'Prompt column', 'Adding Prompt', 'Added Prompt', 
                                            'auto-add', 'existing headers', 'new data headers'
                                        ]):
                                            print(f"      🎯 {log}")
                                
                                break
        
        else:
            print(f"❌ Failed to get instances: {instances_response.status_code}")
    
    except Exception as e:
        print(f"💥 Error: {e}")

def check_current_worksheets():
    """Check current state of worksheets to see Prompt column status"""
    print(f"\n🔍 CHECKING CURRENT WORKSHEET STATUS")
    print("="*40)
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        import os
        
        # Set up credentials
        credentials_path = "credentials.json"  # We're in backend directory
        
        if not os.path.exists(credentials_path):
            print(f"❌ Credentials not found: {credentials_path}")
            return
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet = client.open_by_key(sheet_id)
        
        # Check key worksheets
        key_worksheets = ["TEST121", "YES", "TEST_NEW", "HEYHEY"]
        
        for worksheet_name in key_worksheets[:3]:  # Check first 3
            try:
                worksheet = sheet.worksheet(worksheet_name)
                
                # Get headers
                headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
                
                print(f"\n📄 {worksheet_name}:")
                print(f"   Headers: {headers}")
                
                if "Prompt" in headers:
                    prompt_col_index = headers.index("Prompt")
                    print(f"   🎯 Prompt column at index {prompt_col_index} ✅")
                    
                    # Count non-empty Prompt cells
                    all_values = worksheet.get_all_values()
                    prompt_count = 0
                    
                    for row in all_values[1:]:  # Skip header
                        if len(row) > prompt_col_index and row[prompt_col_index].strip():
                            prompt_count += 1
                    
                    print(f"   💬 Rows with Prompt data: {prompt_count}")
                    
                    if prompt_count > 0:
                        # Show latest Prompt entry
                        for i in range(len(all_values) - 1, 0, -1):
                            row = all_values[i]
                            if len(row) > prompt_col_index and row[prompt_col_index].strip():
                                print(f"   📝 Latest: {row[prompt_col_index][:80]}...")
                                break
                else:
                    print(f"   ❌ No Prompt column found")
                    
            except gspread.WorksheetNotFound:
                print(f"\n📄 {worksheet_name}: Not found")
            except Exception as e:
                print(f"\n📄 {worksheet_name}: Error - {e}")
    
    except Exception as e:
        print(f"💥 Error checking worksheets: {e}")

if __name__ == "__main__":
    test_simple_workflow_with_prompt()
    check_current_worksheets()
    
    print(f"\n💡 EXPECTED BEHAVIOR:")
    print(f"✅ Auto-add Prompt column to worksheets that don't have it")
    print(f"✅ Write AI_Response data to Prompt column")
    print(f"✅ Preserve existing data in other columns")
