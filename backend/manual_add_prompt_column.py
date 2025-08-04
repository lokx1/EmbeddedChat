#!/usr/bin/env python3
"""
Manually add Prompt column to worksheets and test workflow
"""

import gspread
from google.oauth2.service_account import Credentials

def add_prompt_column_to_worksheets():
    """Manually add Prompt column to worksheets that don't have it"""
    print("🔧 MANUALLY ADDING PROMPT COLUMN TO WORKSHEETS")
    print("="*50)
    
    try:
        # Set up credentials
        credentials_path = "credentials.json"
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet = client.open_by_key(sheet_id)
        
        # Target worksheets to add Prompt column
        target_worksheets = ["TEST121", "YES", "TEST_NEW"]
        
        for worksheet_name in target_worksheets:
            try:
                worksheet = sheet.worksheet(worksheet_name)
                
                print(f"\n📄 Processing {worksheet_name}...")
                
                # Get current headers
                headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
                
                print(f"   📊 Current headers: {headers}")
                
                if "Prompt" not in headers:
                    # Add Prompt column
                    next_col = len(headers) + 1
                    next_col_letter = chr(ord('A') + next_col - 1)
                    
                    print(f"   🎯 Adding Prompt column at {next_col_letter}1")
                    
                    # Add header
                    worksheet.update(f"{next_col_letter}1", "Prompt")
                    
                    print(f"   ✅ Added Prompt column to {worksheet_name}")
                else:
                    print(f"   ✅ {worksheet_name} already has Prompt column")
                    
            except gspread.WorksheetNotFound:
                print(f"\n📄 {worksheet_name}: Not found")
            except Exception as e:
                print(f"\n📄 {worksheet_name}: Error - {e}")
    
    except Exception as e:
        print(f"💥 Error: {e}")

def verify_prompt_columns_added():
    """Verify Prompt columns were added successfully"""
    print(f"\n🔍 VERIFYING PROMPT COLUMNS ADDED")
    print("="*35)
    
    try:
        # Set up credentials
        credentials_path = "credentials.json"
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
        sheet = client.open_by_key(sheet_id)
        
        target_worksheets = ["TEST121", "YES", "TEST_NEW"]
        
        for worksheet_name in target_worksheets:
            try:
                worksheet = sheet.worksheet(worksheet_name)
                
                # Get headers
                headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
                
                print(f"\n📄 {worksheet_name}:")
                print(f"   Headers: {headers}")
                
                if "Prompt" in headers:
                    prompt_index = headers.index("Prompt")
                    print(f"   🎯 Prompt column at index {prompt_index} ✅")
                else:
                    print(f"   ❌ No Prompt column found")
                    
            except gspread.WorksheetNotFound:
                print(f"\n📄 {worksheet_name}: Not found")
            except Exception as e:
                print(f"\n📄 {worksheet_name}: Error - {e}")
    
    except Exception as e:
        print(f"💥 Error: {e}")

def create_workflow_with_prompt_target():
    """Create a workflow instance that targets a worksheet with Prompt column"""
    print(f"\n🚀 TESTING WORKFLOW WITH PROMPT-ENABLED WORKSHEET")
    print("="*50)
    
    import requests
    
    base_url = "http://localhost:8000/api/v1"
    
    # Create simple workflow execution by triggering existing instance
    instance_id = "992ca1c0-6317-42c6-a613-368eedacd5c4"
    
    try:
        # Check current instance
        response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
        
        if response.status_code == 200:
            instance_data = response.json()
            instance = instance_data["data"]
            
            print(f"📊 Instance: {instance['name']}")
            print(f"📊 Status: {instance['status']}")
            
            # Execute workflow again
            print(f"\n🚀 Executing workflow...")
            
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            
            if execute_response.status_code == 200:
                print(f"✅ Workflow execution started")
                return True
            else:
                print(f"❌ Failed to execute: {execute_response.status_code}")
                return False
        else:
            print(f"❌ Failed to get instance: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

if __name__ == "__main__":
    # Step 1: Add Prompt columns manually
    add_prompt_column_to_worksheets()
    
    # Step 2: Verify columns were added
    verify_prompt_columns_added()
    
    # Step 3: Test workflow with Prompt-enabled worksheets
    workflow_started = create_workflow_with_prompt_target()
    
    if workflow_started:
        print(f"\n💡 NEXT STEPS:")
        print(f"1. Wait for workflow to complete (~10-15 seconds)")
        print(f"2. Check worksheets for AI_Response data in Prompt column")
        print(f"3. Run: python check_prompt_columns.py")
    else:
        print(f"\n❌ Workflow execution failed")
    
    print(f"\n🎯 EXPECTED RESULT:")
    print(f"✅ Worksheets now have Prompt column")
    print(f"✅ Workflow should write AI_Response to Prompt column")
    print(f"✅ Data should appear in TEST121 (default target worksheet)")
