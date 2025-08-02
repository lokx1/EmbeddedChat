#!/usr/bin/env python3
"""Check workflow instance configuration"""

import requests
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    # Get latest instance
    r = requests.get('http://localhost:8000/api/v1/workflow/instances')
    instances = r.json()['data']['instances']
    latest = instances[0]
    
    print(f'Instance ID: {latest["id"]}')
    print(f'Name: {latest["name"]}')
    print(f'Template ID: {latest["template_id"]}')
    print(f'Status: {latest["status"]}')
    
    # Get full instance data
    detail_r = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{latest["id"]}')
    if detail_r.status_code == 200:
        detail_data = detail_r.json()
        if 'data' in detail_data and 'data' in detail_data['data']:
            workflow_data = detail_data['data']['data']
            if 'nodes' in workflow_data:
                nodes = workflow_data['nodes']
                
                # Find GoogleSheetsWrite nodes
                sheets_nodes = [node for node in nodes if node.get('type') == 'GoogleSheetsWrite']
                if sheets_nodes:
                    print(f'\n📋 Found {len(sheets_nodes)} GoogleSheetsWrite node(s):')
                    for i, node in enumerate(sheets_nodes):
                        config = node.get('data', {}).get('config', {})
                        print(f'  Node {i+1}: {config}')
                else:
                    print('\n❌ No GoogleSheetsWrite nodes found')
            else:
                print('\n❌ No nodes data found')
        else:
            print('\n❌ No workflow data found')
    else:
        print(f'\n❌ Failed to get instance details: {detail_r.status_code}')

if __name__ == "__main__":
    main()
