#!/usr/bin/env python3
"""
Test Enhanced AI Response Generation
Test với higher token limit và enhanced prompt
"""

import requests
import time
import json

def trigger_enhanced_workflow():
    """Trigger workflow với enhanced settings"""
    
    print("🚀 Triggering Enhanced AI Workflow...")
    print("📋 Settings:")
    print("   - Max Tokens: 4000 (increased from 1000)")
    print("   - Enhanced Prompt: Comprehensive asset specification")
    print("   - Expected: Longer, more detailed AI responses")
    
    try:
        # Trigger workflow
        response = requests.post("http://localhost:8000/api/workflows/execute", 
                                json={"workflow_id": "test_workflow"})
        
        if response.status_code == 200:
            execution_id = response.json().get("execution_id")
            print(f"✅ Workflow triggered: {execution_id}")
            
            print("⏳ Waiting 30 seconds for enhanced AI processing...")
            for i in range(30):
                print(f"   {30-i} seconds remaining...", end='\r')
                time.sleep(1)
            print("\n")
            
            # Check status
            status_response = requests.get(f"http://localhost:8000/api/workflows/status/{execution_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"📊 Final Status: {status_data.get('status')}")
                
                if status_data.get('status') == 'completed':
                    print("✅ Enhanced workflow completed!")
                    print("📋 Next steps:")
                    print("   1. Check backend logs for debug output")
                    print("   2. Check Google Sheets HEY worksheet")
                    print("   3. Verify Prompt column has detailed AI responses")
                    return True
                else:
                    print(f"❌ Workflow status: {status_data.get('status')}")
                    
        else:
            print(f"❌ Failed to trigger: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def check_sheets_for_enhanced_responses():
    """Check if enhanced responses are in Google Sheets"""
    
    print("\n🔍 Checking Google Sheets for enhanced responses...")
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
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
                
                # Check for enhanced AI responses
                enhanced_responses = 0
                for i, row in enumerate(all_values[1:], 2):
                    if len(row) > prompt_col_idx:
                        prompt_value = row[prompt_col_idx] if prompt_col_idx < len(row) else ""
                        if prompt_value and len(prompt_value) > 500:  # Enhanced response should be longer
                            enhanced_responses += 1
                            print(f"✅ Row {i}: Enhanced AI Response ({len(prompt_value)} chars)")
                            print(f"   Preview: {prompt_value[:200]}...")
                        elif prompt_value:
                            print(f"⚠️ Row {i}: Short response ({len(prompt_value)} chars)")
                        else:
                            print(f"❌ Row {i}: Empty response")
                
                print(f"\n📊 Summary:")
                print(f"   - Total rows with enhanced responses: {enhanced_responses}")
                print(f"   - Expected: 4 rows with detailed responses")
                
                return enhanced_responses > 0
            else:
                print("❌ Prompt column not found")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    return False

if __name__ == "__main__":
    print("🎯 Enhanced AI Response Test")
    print("="*60)
    
    # Trigger enhanced workflow
    success = trigger_enhanced_workflow()
    
    if success:
        # Check results
        enhanced_found = check_sheets_for_enhanced_responses()
        
        print("\n" + "="*60)
        if enhanced_found:
            print("🎉 SUCCESS: Enhanced AI responses generated!")
            print("📊 Token limit increase and enhanced prompt are working!")
        else:
            print("⚠️ Enhanced responses not found - check backend logs for issues")
    else:
        print("❌ Failed to trigger enhanced workflow")
