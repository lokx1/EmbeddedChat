"""
Check workflow logs via API
"""

import requests
import json

def check_workflow_logs():
    """Check latest workflow logs via API"""
    print("🔍 Checking workflow execution logs via API...")
    
    try:
        base_url = "http://localhost:8000/api/v1"
        
        # Get recent instances
        response = requests.get(f"{base_url}/workflow/instances?limit=5")
        if response.status_code == 200:
            data = response.json()
            instances = data.get('data', {}).get('instances', [])
            
            print(f"📊 Found {len(instances)} recent instances:")
            
            for i, instance in enumerate(instances, 1):
                print(f"\n📝 Instance {i}:")
                print(f"   ID: {instance['id']}")
                print(f"   Status: {instance['status']}")
                print(f"   Template: {instance.get('template_name', 'N/A')}")
                print(f"   Created: {instance.get('created_at', 'N/A')}")
                
                # Get detailed instance info
                detail_response = requests.get(f"{base_url}/workflow/instances/{instance['id']}")
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    instance_detail = detail_data.get('data', {}).get('instance', {})
                    
                    print(f"   Error: {instance_detail.get('error_message', 'None')}")
                    
                    # Get execution logs
                    logs_response = requests.get(f"{base_url}/workflow/instances/{instance['id']}/logs")
                    if logs_response.status_code == 200:
                        logs_data = logs_response.json()
                        steps = logs_data.get('data', {}).get('steps', [])
                        
                        print(f"   📊 Execution Steps ({len(steps)}):")
                        for j, step in enumerate(steps, 1):
                            print(f"      Step {j}: {step.get('step_type', 'Unknown')} - {step.get('status', 'Unknown')}")
                            if step.get('error_message'):
                                print(f"         Error: {step['error_message']}")
                            if step.get('output_data'):
                                print(f"         Output: {json.dumps(step['output_data'], indent=8)}")
                    else:
                        print(f"   ❌ Failed to get logs: {logs_response.status_code}")
                else:
                    print(f"   ❌ Failed to get details: {detail_response.status_code}")
        else:
            print(f"❌ Failed to get instances: {response.status_code}")
            print(f"   Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error checking logs: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_workflow_logs()
