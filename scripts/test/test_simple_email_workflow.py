#!/usr/bin/env python3
"""
Simple test để gửi email qua workflow manual execution
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8000/api/v1"

def test_simple_email_workflow():
    print("🚀 SIMPLE EMAIL WORKFLOW TEST")
    print("=" * 50)
    
    try:
        # 1. Create simple template
        print("1️⃣ Creating workflow template...")
        template_data = {
            "name": "Simple Email Test",
            "description": "Simple email report test",
            "metadata": {"version": "1.0"},
            "workflow_data": {
                "nodes": [
                    {
                        "id": "email_only",
                        "type": "email_report",
                        "data": {
                            "recipient_email": "longbaoluu68@gmail.com",
                            "report_type": "execution",
                            "include_charts": True
                        },
                        "position": {"x": 100, "y": 100}
                    }
                ],
                "edges": []
            }
        }
        
        resp = requests.post(f"{BACKEND_URL}/workflow/templates/", json=template_data)
        print(f"Template response: {resp.status_code}")
        if resp.status_code == 200:
            template = resp.json()
            template_id = template.get("template_id")
            print(f"✅ Template created: {template_id}")
            
            # 2. Create instance
            print("\n2️⃣ Creating instance...")
            instance_data = {
                "template_id": template_id,
                "name": "Email Test Instance"
            }
            
            resp = requests.post(f"{BACKEND_URL}/workflow/instances/", json=instance_data)
            print(f"Instance response: {resp.status_code}")
            if resp.status_code == 200:
                instance = resp.json()
                instance_id = instance.get("instance_id")
                print(f"✅ Instance created: {instance_id}")
                
                # 3. Execute
                print("\n3️⃣ Executing...")
                resp = requests.post(f"{BACKEND_URL}/workflow/instances/{instance_id}/execute")
                print(f"Execute response: {resp.status_code}")
                if resp.status_code == 200:
                    print("✅ Execution started")
                    
                    # 4. Check logs
                    print("\n4️⃣ Checking logs...")
                    time.sleep(5)  # Wait a bit
                    resp = requests.get(f"{BACKEND_URL}/workflow/instances/{instance_id}/logs")
                    if resp.status_code == 200:
                        logs = resp.json()
                        steps = logs.get("logs", [])
                        print(f"📋 Found {len(steps)} execution steps:")
                        for step in steps:
                            name = step.get("step_name", "unknown")
                            status = step.get("status", "unknown")
                            error = step.get("error_message", "")
                            print(f"   - {name}: {status}")
                            if error:
                                print(f"     Error: {error}")
                        
                        # Check if email step succeeded
                        email_steps = [s for s in steps if "Email" in s.get("step_name", "")]
                        if email_steps:
                            email_step = email_steps[0]
                            if email_step.get("status") == "completed":
                                print("✅ EMAIL SENT SUCCESSFULLY! 📧")
                                print("Check longbaoluu68@gmail.com")
                            else:
                                print("❌ Email step failed")
                        else:
                            print("❌ No email steps found")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_email_workflow()
