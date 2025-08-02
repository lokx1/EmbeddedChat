#!/usr/bin/env python3
"""
Check latest workflow execution from frontend
"""

import requests
import json
from datetime import datetime

def check_latest_execution():
    """Check the most recent workflow execution"""
    
    # Get the most recent instance
    response = requests.get('http://localhost:8000/api/v1/workflow/instances')
    if response.status_code == 200:
        instances = response.json()['data']['instances']
        if instances:
            latest = instances[0]  # Most recent
            instance_id = latest['id']
            print(f"🔍 Latest instance: {instance_id}")
            print(f"📝 Name: {latest['name']}")
            print(f"📊 Status: {latest['status']}")
            print(f"🕐 Created: {latest['created_at']}")
            
            # Get instance details
            detail_response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}')
            if detail_response.status_code == 200:
                detail = detail_response.json()['data']['instance']
                
                if detail.get('output_data'):
                    print("\n📤 Output Data:")
                    output = detail['output_data']
                    if 'node_outputs' in output:
                        for node_id, node_output in output['node_outputs'].items():
                            print(f"  {node_id}: {node_output.get('status', 'unknown')}")
                            
                if detail.get('error_message'):
                    print(f"\n❌ Error: {detail['error_message']}")
            
            # Get detailed execution logs
            logs_response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs')
            if logs_response.status_code == 200:
                logs_data = logs_response.json()['data']
                steps = logs_data.get('steps', [])
                print(f"\n📝 Execution steps: {len(steps)}")
                
                for step in steps[-10:]:  # Last 10 steps
                    print(f"\\n[{step['created_at']}] {step['step_type']}: {step['status']}")
                    if step.get('error_message'):
                        print(f"  ❌ Error: {step['error_message']}")
                    if step.get('logs'):
                        for log in step['logs'][-3:]:  # Last 3 logs per step
                            print(f"  📝 {log}")
                    if step.get('output_data'):
                        print(f"  📤 Output keys: {list(step['output_data'].keys())}")
                        
                return True
            else:
                print(f"❌ Failed to get logs: {logs_response.text}")
                return False
        else:
            print("No workflow instances found")
            return False
    else:
        print(f"❌ Failed to get instances: {response.text}")
        return False

if __name__ == "__main__":
    print("=== Latest Workflow Execution Check ===\\n")
    check_latest_execution()
