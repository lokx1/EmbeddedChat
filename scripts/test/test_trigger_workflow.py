#!/usr/bin/env python3
"""
Quick test để trigger workflow và check debug output
"""

import requests
import time

def trigger_workflow_and_check():
    """Trigger workflow để test AI response extraction"""
    
    print("🚀 Triggering workflow to test AI response extraction...")
    
    try:
        # Trigger workflow
        response = requests.post("http://localhost:8000/api/workflows/execute", 
                                json={"workflow_id": "test_workflow"})
        
        if response.status_code == 200:
            execution_id = response.json().get("execution_id")
            print(f"✅ Workflow triggered: {execution_id}")
            
            print("⏳ Waiting 20 seconds for execution...")
            time.sleep(20)
            
            # Check status
            status_response = requests.get(f"http://localhost:8000/api/workflows/status/{execution_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"📊 Final Status: {status_data.get('status')}")
                return True
                
        else:
            print(f"❌ Failed to trigger: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

if __name__ == "__main__":
    print("🧪 Testing AI Response Extraction")
    print("="*50)
    
    success = trigger_workflow_and_check()
    
    if success:
        print("✅ Check backend logs for debug output!")
        print("📋 Then check Google Sheets to see if Prompt column has data")
    else:
        print("❌ Failed to trigger workflow")
