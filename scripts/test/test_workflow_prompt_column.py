#!/usr/bin/env python3
"""
Trigger workflow và monitor kết quả
"""

import requests
import time
import json

def trigger_workflow_test():
    """Trigger workflow và check kết quả"""
    
    print("🚀 Triggering workflow to test Prompt column...")
    
    # Trigger workflow
    try:
        response = requests.post("http://localhost:8000/api/workflows/execute", 
                                json={"workflow_id": "test_workflow"})
        
        if response.status_code == 200:
            execution_id = response.json().get("execution_id")
            print(f"✅ Workflow triggered: {execution_id}")
            
            # Wait a bit for execution
            print("⏳ Waiting for execution to complete...")
            time.sleep(15)
            
            # Check status
            status_response = requests.get(f"http://localhost:8000/api/workflows/status/{execution_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"📊 Status: {status_data.get('status')}")
                
                if status_data.get('status') == 'completed':
                    print("✅ Workflow completed!")
                    return True
                    
        else:
            print(f"❌ Failed to trigger workflow: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def check_prompt_in_hey():
    """Check nếu Prompt column đã được ghi data"""
    
    print("🔍 Checking Prompt column in HEY worksheet...")
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))
    
    import gspread
    from google.oauth2.service_account import Credentials
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        creds = Credentials.from_service_account_file(
            'backend/credentials.json', 
            scopes=SCOPES
        )
        gc = gspread.authorize(creds)
        
        # Open sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.worksheet("HEY")
        
        # Get all data
        all_values = worksheet.get_all_values()
        
        if len(all_values) > 0:
            headers = all_values[0]
            print(f"📋 Headers: {headers}")
            
            if "Prompt" in headers:
                prompt_col_idx = headers.index("Prompt")
                print(f"✅ Prompt column at index {prompt_col_idx}")
                
                # Check for AI responses
                ai_responses_found = 0
                for i, row in enumerate(all_values[1:], 2):
                    if len(row) > prompt_col_idx:
                        prompt_value = row[prompt_col_idx] if prompt_col_idx < len(row) else ""
                        if prompt_value and len(prompt_value) > 10:  # Non-empty response
                            ai_responses_found += 1
                            print(f"✅ Row {i}: AI Response found - {prompt_value[:100]}...")
                        else:
                            print(f"❌ Row {i}: Empty or short response")
                
                print(f"📊 Total AI responses found: {ai_responses_found}")
                return ai_responses_found > 0
            else:
                print("❌ Prompt column not found")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    return False

if __name__ == "__main__":
    print("🎯 Test Workflow with Prompt Column")
    print("="*50)
    
    # First check current state
    print("📊 Checking current state...")
    has_ai_responses = check_prompt_in_hey()
    
    if not has_ai_responses:
        print("\n🚀 Triggering new workflow execution...")
        success = trigger_workflow_test()
        
        if success:
            print("\n🔍 Checking results after workflow...")
            check_prompt_in_hey()
    else:
        print("✅ AI responses already found in Prompt column!")
    
    print("\n" + "="*50)
    print("🎯 Test completed!")
