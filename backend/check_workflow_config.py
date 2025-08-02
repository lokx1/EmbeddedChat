#!/usr/bin/env python3
"""Check workflow instance configuration"""

import requests
import json

def main():
    print("🔍 Checking Workflow Instance Configuration")
    print("=" * 50)
    
    try:
        # Get latest instance
        response = requests.get("http://localhost:8000/api/v1/workflow/instances")
        if response.status_code == 200:
            instances = response.json()
            if instances:
                latest = instances[-1]
                print(f"📋 Latest instance: {latest['id']}")
                print(f"📝 Name: {latest.get('name', 'Unknown')}")
                print(f"📊 Status: {latest.get('status', 'Unknown')}")
                
                # Check workflow data
                if 'data' in latest and 'nodes' in latest['data']:
                    nodes = latest['data']['nodes']
                    print(f"\n📦 Found {len(nodes)} nodes:")
                    
                    for node in nodes:
                        node_type = node.get('type', 'Unknown')
                        print(f"  - {node_type}")
                        
                        if node_type == 'GoogleSheetsWrite':
                            config = node.get('data', {}).get('config', {})
                            print(f"    📋 GoogleSheetsWrite config:")
                            for key, value in config.items():
                                print(f"      {key}: {value}")
                else:
                    print("❌ No workflow data found")
            else:
                print("❌ No instances found")
        else:
            print(f"❌ Failed to get instances: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
