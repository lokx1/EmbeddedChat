#!/usr/bin/env python3
"""
Trigger workflow và check Prompt column result ngay lập tức
"""

import requests
import time
import gspread
from google.oauth2.service_account import Credentials

def trigger_workflow():
    """Trigger workflow execution"""
    
    print("🚀 Triggering workflow...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/workflows/execute", 
            json={"workflow_id": "test_workflow"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            execution_id = result.get("execution_id")
            print(f"✅ Workflow triggered with ID: {execution_id}")
            return execution_id
        else:
            print(f"❌ Failed to trigger: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error triggering workflow: {e}")
        return None

def wait_for_completion(execution_id, max_wait=30):
    """Wait for workflow completion"""
    
    print(f"⏳ Waiting for workflow {execution_id} to complete...")
    
    for i in range(max_wait):
        try:
            response = requests.get(f"http://localhost:8000/api/workflows/status/{execution_id}")
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status')
                print(f"📊 Status: {status} ({i+1}/{max_wait})")
                
                if status == 'completed':
                    print("✅ Workflow completed!")
                    return True
                elif status == 'failed':
                    print("❌ Workflow failed!")
                    return False
                    
        except Exception as e:
            print(f"⚠️ Error checking status: {e}")
            
        time.sleep(1)
    
    print("⏰ Timeout waiting for completion")
    return False

def check_prompt_column_immediately():
    """Check Prompt column trong worksheet HEY ngay lập tức"""
    
    print("🔍 Checking Prompt column in HEY worksheet...")
    
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
        
        print(f"📊 Total rows in HEY: {len(all_values)}")
        
        if len(all_values) > 0:
            headers = all_values[0]
            print(f"📋 Headers: {headers}")
            
            if "Prompt" in headers:
                prompt_idx = headers.index("Prompt")
                print(f"✅ Prompt column found at index {prompt_idx}")
                
                # Check recent changes - look for AI responses
                ai_responses_found = 0
                total_data_rows = 0
                
                for i, row in enumerate(all_values[1:], 2):
                    total_data_rows += 1
                    if len(row) > prompt_idx:
                        prompt_value = row[prompt_idx] if prompt_idx < len(row) else ""
                        if prompt_value and len(prompt_value.strip()) > 20:  # Substantial content
                            ai_responses_found += 1
                            print(f"✅ Row {i}: AI Response ({len(prompt_value)} chars) - {prompt_value[:100]}...")
                        elif prompt_value:
                            print(f"ℹ️ Row {i}: Short content ({len(prompt_value)} chars) - {prompt_value}")
                        else:
                            print(f"❌ Row {i}: Empty Prompt")
                
                print(f"\n📊 Summary:")
                print(f"   Total data rows: {total_data_rows}")
                print(f"   Rows with AI responses: {ai_responses_found}")
                print(f"   Success rate: {ai_responses_found/total_data_rows*100:.1f}%" if total_data_rows > 0 else "   No data rows")
                
                return ai_responses_found > 0
            else:
                print(f"❌ Prompt column not found in headers")
                return False
        else:
            print(f"❌ No data in worksheet")
            return False
                
    except Exception as e:
        print(f"❌ Error checking sheet: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎯 Quick Workflow Test - Auto Prompt Column")
    print("="*60)
    
    # Check current state first
    print("📊 Checking current state of Prompt column...")
    current_state = check_prompt_column_immediately()
    
    if current_state:
        print("✅ Prompt column already has AI responses!")
        print("📋 If you want to test again, clear the data and re-run.")
        return
    
    print("\n🚀 Current state shows no AI responses, triggering new workflow...")
    
    # Trigger workflow
    execution_id = trigger_workflow()
    if not execution_id:
        print("❌ Failed to trigger workflow")
        return
    
    # Wait for completion
    completed = wait_for_completion(execution_id, max_wait=45)
    
    if not completed:
        print("⏰ Workflow did not complete in time")
        return
    
    # Check results
    print("\n🔍 Checking results after workflow completion...")
    time.sleep(2)  # Give a moment for data to sync
    
    success = check_prompt_column_immediately()
    
    print("\n" + "="*60)
    if success:
        print("🎉 SUCCESS! Auto-add Prompt column is working correctly!")
        print("✅ AI responses have been written to the Prompt column.")
    else:
        print("❌ ISSUE: Prompt column not populated with AI responses")
        print("📋 This indicates a problem in the workflow data flow")

if __name__ == "__main__":
    main()
