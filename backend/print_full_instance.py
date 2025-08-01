#!/usr/bin/env python3
"""
Print Full Instance Details
"""

import requests
import json

def print_full_instance():
    """Print full instance details for debugging"""
    base_url = "http://localhost:8000/api/v1/workflow"
    
    try:
        # Get all instances
        response = requests.get(f"{base_url}/instances")
        data = response.json()
        instances = data.get("data", {}).get("instances", [])
        
        # Find latest Qwen instance
        qwen_instances = [
            inst for inst in instances 
            if "qwen" in inst.get("name", "").lower()
        ]
        
        if qwen_instances:
            latest = qwen_instances[0]
            instance_id = latest.get("id")
            
            # Get detailed instance info
            detail_response = requests.get(f"{base_url}/instances/{instance_id}")
            detail_data = detail_response.json()
            
            print("🔍 Full Instance Details:")
            print("="*50)
            print(json.dumps(detail_data, indent=2))
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print_full_instance()
