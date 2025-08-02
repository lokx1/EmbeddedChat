#!/usr/bin/env python3
"""Check workflow template configuration"""

import requests
import json

def main():
    template_id = "9cd9573b-e1f9-4dab-be21-d00920cf5f17"
    
    r = requests.get(f'http://localhost:8000/api/v1/workflow/templates/{template_id}')
    if r.status_code == 200:
        template_data = r.json()
        template = template_data['template']
        
        print(f'Template Name: {template["name"]}')
        print(f'Description: {template["description"]}')
        
        if 'template_data' in template and 'nodes' in template['template_data']:
            nodes = template['template_data']['nodes']
            
            # Find GoogleSheetsWrite nodes
            sheets_nodes = [node for node in nodes if node.get('type') == 'google_sheets_write']
            if sheets_nodes:
                print(f'\n📋 Found {len(sheets_nodes)} GoogleSheetsWrite node(s):')
                for i, node in enumerate(sheets_nodes):
                    config = node.get('data', {}).get('config', {})
                    print(f'  Node {i+1}:')
                    print(f'    Full config: {json.dumps(config, indent=4)}')
            else:
                print('\n❌ No GoogleSheetsWrite nodes found')
                print('\nAll nodes:')
                for node in nodes:
                    print(f'  - {node.get("type")}: {node.get("id")}')
        else:
            print('\n❌ No template data found')
    else:
        print(f'❌ Failed to get template: {r.status_code}')

if __name__ == "__main__":
    main()
