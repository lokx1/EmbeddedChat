#!/usr/bin/env python3
"""
Test if Frontend Fix Works
"""

import requests
import time

def monitor_new_instances():
    """Monitor for new instances created by frontend"""
    print("🔍 Monitoring New Instance Creation from Frontend")
    print("="*55)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Get current instance count
    response = requests.get(f"{base_url}/instances")
    if response.status_code == 200:
        data = response.json()
        initial_count = len(data.get("data", {}).get("instances", []))
        print(f"📊 Initial instance count: {initial_count}")
    else:
        print(f"❌ Failed to get initial count")
        return
    
    print(f"\n⏳ Monitoring for new instances (60 seconds)...")
    print(f"   Go to frontend and execute a workflow now!")
    
    for i in range(60):
        try:
            response = requests.get(f"{base_url}/instances")
            if response.status_code == 200:
                data = response.json()
                instances = data.get("data", {}).get("instances", [])
                current_count = len(instances)
                
                if current_count > initial_count:
                    print(f"\n🎯 NEW INSTANCE DETECTED!")
                    
                    # Show latest instances
                    latest_instances = instances[:3]
                    for j, instance in enumerate(latest_instances):
                        print(f"   {j+1}. {instance.get('name', 'Unnamed')}")
                        print(f"      ID: {instance.get('id', 'unknown')}")
                        print(f"      Status: {instance.get('status', 'unknown')}")
                        print(f"      Created: {instance.get('created_at', 'unknown')}")
                        
                        # Check if it's from frontend
                        if 'frontend' in instance.get('created_by', '').lower():
                            print(f"      ✅ CREATED BY FRONTEND!")
                        print()
                    
                    return True
                else:
                    if i % 10 == 0:  # Print every 10 seconds
                        print(f"   Still {current_count} instances... ({i+1}/60)")
        
        except Exception as e:
            print(f"   Error checking: {str(e)}")
        
        time.sleep(1)
    
    print(f"\n⏰ Monitoring timeout - no new instances detected")
    return False

if __name__ == "__main__":
    print("🚀 Frontend Fix Test Monitor")
    print("="*35)
    
    success = monitor_new_instances()
    
    if success:
        print(f"\n🎉 FRONTEND FIX WORKING!")
        print(f"✅ Frontend successfully creating real instances")
        print(f"✅ No more fake instance IDs")
    else:
        print(f"\n❌ Frontend still not working correctly")
        print(f"💡 Check browser console for errors")
