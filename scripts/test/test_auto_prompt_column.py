#!/usr/bin/env python3
"""
Test Auto-Add Prompt Column Feature
"""

import requests
import json
import time

def test_auto_prompt_column():
    """Test workflow with auto-add Prompt column to any worksheet"""
    print("🚀 TESTING AUTO-ADD PROMPT COLUMN FEATURE")
    print("="*55)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test with different worksheets
    test_worksheets = [
        "TEST121",     # Default worksheet (no Prompt column)
        "YES",         # Another worksheet (no Prompt column)  
        "NEW_AUTO_PROMPT"  # New worksheet (will be created)
    ]
    
    for worksheet_name in test_worksheets:
        print(f"\n🔸 Testing worksheet: {worksheet_name}")
        print("="*40)
        
        # Create workflow instance
        instance_data = {
            "name": f"Auto Prompt Test - {worksheet_name} - " + 
                   __import__('datetime').datetime.now().strftime("%H:%M:%S"),
            "description": f"Test auto-add Prompt column to {worksheet_name}",
            "template_id": "1643d9b9-82a7-4fe0-a56d-11f96a922d0f",  # Use existing AI template
            "config_overrides": {
                "google_sheets_write": {
                    "worksheet_name": worksheet_name,
                    "mode": "overwrite"
                },
                "google_sheets": {
                    "worksheet_name": worksheet_name
                }
            }
        }
        
        try:
            # Create instance
            instance_response = requests.post(
                f"{base_url}/workflow/instances",
                json=instance_data
            )
            
            if instance_response.status_code == 201:
                instance_resp_data = instance_response.json()
                instance_id = instance_resp_data["data"]["id"]
                print(f"✅ Created instance: {instance_id[:8]}...")
                
                # Execute workflow
                execute_response = requests.post(
                    f"{base_url}/workflow/instances/{instance_id}/execute"
                )
                
                if execute_response.status_code == 200:
                    print(f"🚀 Workflow started for {worksheet_name}")
                    
                    # Wait for completion
                    max_wait = 20
                    wait_time = 0
                    
                    while wait_time < max_wait:
                        status_response = requests.get(
                            f"{base_url}/workflow/instances/{instance_id}"
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            status = status_data["data"]["status"]
                            
                            if status == "completed":
                                print(f"🎉 Workflow completed for {worksheet_name}!")
                                
                                # Check results
                                logs_response = requests.get(
                                    f"{base_url}/workflow/instances/{instance_id}/logs"
                                )
                                
                                if logs_response.status_code == 200:
                                    logs_data = logs_response.json()
                                    steps = logs_data.get("data", {}).get("steps", [])
                                    
                                    for step in steps:
                                        if step['step_type'] == 'google_sheets_write':
                                            output = step.get('output_data', {})
                                            operation = output.get('operation')
                                            status = output.get('status')
                                            
                                            print(f"   📝 Sheets Write: {operation} -> {status}")
                                            
                                            if status == 'success':
                                                data_written = output.get('data_written', {})
                                                rows_count = data_written.get('rows_count', 0)
                                                range_written = data_written.get('range_written', 'N/A')
                                                
                                                print(f"      ✅ Wrote {rows_count} rows")
                                                print(f"      📍 Range: {range_written}")
                                                print(f"      🎯 Worksheet: {worksheet_name}")
                                            
                                            # Check logs for Prompt column creation
                                            if step.get('logs'):
                                                for log in step['logs']:
                                                    if "Adding Prompt column" in log or "Added Prompt column" in log:
                                                        print(f"      🎯 {log}")
                                break
                                
                            elif status == "failed":
                                print(f"❌ Workflow failed for {worksheet_name}")
                                break
                        
                        time.sleep(1)
                        wait_time += 1
                    
                    if wait_time >= max_wait:
                        print(f"⏰ Timeout waiting for {worksheet_name}")
                
                else:
                    print(f"❌ Failed to execute for {worksheet_name}: {execute_response.status_code}")
                    print(f"Response: {execute_response.text}")
            
            else:
                print(f"❌ Failed to create instance for {worksheet_name}: {instance_response.status_code}")
                print(f"Response: {instance_response.text}")
                
        except Exception as e:
            print(f"💥 Error testing {worksheet_name}: {e}")
        
        print()  # Add spacing between tests

def verify_prompt_columns():
    """Verify Prompt columns were added to worksheets"""
    print(f"\n🔍 VERIFYING PROMPT COLUMNS ADDED")
    print("="*40)
    
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
        
        test_worksheets = ["TEST121", "YES", "NEW_AUTO_PROMPT"]
        
        for worksheet_name in test_worksheets:
            try:
                worksheet = sheet.worksheet(worksheet_name)
                
                # Get headers
                headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
                
                print(f"\n📄 {worksheet_name}:")
                print(f"   Headers: {headers}")
                
                if "Prompt" in headers:
                    prompt_col_index = headers.index("Prompt")
                    print(f"   🎯 Prompt column at index {prompt_col_index}")
                    
                    # Check for data in Prompt column
                    all_values = worksheet.get_all_values()
                    prompt_data = []
                    
                    for i, row in enumerate(all_values[1:], 1):  # Skip header
                        if len(row) > prompt_col_index and row[prompt_col_index].strip():
                            prompt_data.append((i+1, row[prompt_col_index]))
                    
                    print(f"   💬 Rows with Prompt data: {len(prompt_data)}")
                    
                    if prompt_data:
                        for row_num, prompt in prompt_data[-2:]:  # Show last 2
                            print(f"      Row {row_num}: {prompt[:80]}...")
                else:
                    print(f"   ❌ No Prompt column found")
                    
            except gspread.WorksheetNotFound:
                print(f"\n📄 {worksheet_name}: Not found")
            except Exception as e:
                print(f"\n📄 {worksheet_name}: Error - {e}")
    
    except Exception as e:
        print(f"💥 Error verifying: {e}")

if __name__ == "__main__":
    test_auto_prompt_column()
    verify_prompt_columns()
    
    print(f"\n💡 SUMMARY:")
    print(f"This test checks if the system can automatically add Prompt column")
    print(f"to any worksheet when writing AI_Response data.")
