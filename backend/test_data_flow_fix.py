#!/usr/bin/env python3
"""Create new workflow instance and execute to test the fix"""

import requests
import json
from datetime import datetime

def main():
    print("🚀 Creating New Workflow Instance to Test Data Flow Fix")
    print("=" * 60)
    
    # Use existing template
    template_id = "0130e10e-ec1e-49ed-bb1c-954c20d781a3"
    
    # Create new instance
    instance_data = {
        "name": f"Test Data Flow Fix - {datetime.now().strftime('%H:%M:%S')}",
        "template_id": template_id
    }
    
    try:
        # Create instance
        response = requests.post("http://localhost:8000/api/v1/workflow/instances", json=instance_data)
        if response.status_code == 200:
            instance = response.json()['instance']
            instance_id = instance['id']
            print(f"✅ Created instance: {instance_id}")
            
            # Execute workflow
            print("\n📤 Executing workflow...")
            execute_response = requests.post(f"http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute")
            
            if execute_response.status_code == 200:
                result = execute_response.json()
                print(f"✅ Execution started: {result}")
                print(f"\n⏳ Workflow is running... Monitor the progress in frontend or check logs.")
                print(f"🔗 Instance ID: {instance_id}")
                
                # Wait a bit and check the current status
                import time
                print("\n⌛ Waiting 5 seconds to check initial progress...")
                time.sleep(5)
                
                # Check status
                status_response = requests.get(f"http://localhost:8000/api/v1/workflow/instances/{instance_id}/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"📊 Current status: {status}")
                
                return instance_id
            else:
                print(f"❌ Failed to execute: {execute_response.status_code}")
                print(f"Error: {execute_response.text}")
        else:
            print(f"❌ Failed to create instance: {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    instance_id = main()
    if instance_id:
        print(f"\n📋 Monitor this instance: {instance_id}")
        print("🔗 Check frontend UI or wait for execution to complete")
        print("📄 This workflow should now properly pass data from AI processing to Google Sheets Write")
