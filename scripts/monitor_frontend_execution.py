#!/usr/bin/env python3
"""
Debug frontend issue by checking what happens when Execute is clicked
"""

import requests
import json
import time
from datetime import datetime

def monitor_frontend_execution():
    """Monitor what happens when frontend executes a workflow"""
    
    print("🔍 Monitoring backend for frontend execution...")
    print("👆 Now click Execute in your frontend")
    
    # Get current instance count
    response = requests.get('http://localhost:8000/api/v1/workflow/instances')
    if response.status_code == 200:
        initial_count = len(response.json()['data']['instances'])
        print(f"📊 Current instances: {initial_count}")
    else:
        initial_count = 0
        print("❌ Cannot get initial instance count")
    
    print("\\n⏳ Waiting for new executions (watching for 60 seconds)...")
    
    start_time = time.time()
    last_count = initial_count
    
    while time.time() - start_time < 60:  # Monitor for 60 seconds
        try:
            # Check for new instances
            response = requests.get('http://localhost:8000/api/v1/workflow/instances')
            if response.status_code == 200:
                instances = response.json()['data']['instances']
                current_count = len(instances)
                
                if current_count > last_count:
                    print(f"\\n🆕 New execution detected! ({current_count - last_count} new instances)")
                    
                    # Get the latest instances
                    new_instances = instances[:current_count - last_count]
                    
                    for instance in new_instances:
                        instance_id = instance['id']
                        instance_name = instance['name']
                        print(f"\\n📋 New Instance: {instance_id}")
                        print(f"   Name: {instance_name}")
                        print(f"   Status: {instance['status']}")
                        
                        # Monitor this instance
                        monitor_count = 0
                        while monitor_count < 10:  # Monitor for up to 30 seconds
                            time.sleep(3)
                            monitor_count += 1
                            
                            detail_response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}')
                            if detail_response.status_code == 200:
                                detail = detail_response.json()['data']['instance']
                                status = detail['status']
                                print(f"   [{monitor_count}] Status: {status}")
                                
                                if status in ['completed', 'failed', 'error']:
                                    print(f"   ✅ Final status: {status}")
                                    
                                    # Get execution logs
                                    logs_response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs')
                                    if logs_response.status_code == 200:
                                        logs_data = logs_response.json()['data']
                                        steps = logs_data.get('steps', [])
                                        print(f"   📝 Execution steps: {len(steps)}")
                                        
                                        for step in steps:
                                            step_status = step['status']
                                            step_type = step['step_type']
                                            print(f"      {step_type}: {step_status}")
                                            if step.get('error_message'):
                                                print(f"         ❌ {step['error_message']}")
                                    
                                    break
                                    
                    last_count = current_count
                
        except Exception as e:
            print(f"❌ Error monitoring: {e}")
        
        time.sleep(2)
    
    print(f"\\n⏰ Monitoring finished after 60 seconds")
    print("\\n💡 If no new executions were detected:")
    print("   - Frontend may have JavaScript errors")
    print("   - API calls might be failing")
    print("   - Check browser console for errors")

def check_backend_health():
    """Check if backend is healthy and ready"""
    print("🏥 Checking backend health...")
    
    try:
        # Check components endpoint
        response = requests.get('http://localhost:8000/api/v1/workflow/components')
        if response.status_code == 200:
            components = response.json()['data']
            print(f"✅ Components API: {len(components)} components available")
            
            # Check for required components
            required_types = ['manual_trigger', 'google_sheets', 'google_sheets_write', 'ai_processing']
            available_types = [comp['type'] for comp in components]
            
            for req_type in required_types:
                if req_type in available_types:
                    print(f"   ✅ {req_type}")
                else:
                    print(f"   ❌ {req_type} - MISSING!")
        else:
            print(f"❌ Components API failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")

if __name__ == "__main__":
    print("=== Frontend Execution Debug ===\\n")
    
    # Check backend health first
    check_backend_health()
    
    print("\\n" + "="*50)
    
    # Monitor for frontend executions
    monitor_frontend_execution()
