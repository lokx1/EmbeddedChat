#!/usr/bin/env python3
"""Create workflow instance with Test sheet name"""

import requests
import json
from datetime import datetime

def main():
    print("🚀 Creating new workflow instance with 'Test' sheet name")
    
    # Create workflow instance with Test sheet
    workflow_data = {
        "name": f"Test Sheet Auto-Create - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Test workflow with auto-created Test sheet",
        "template_data": {
            "nodes": [
                {
                    "id": "start-1",
                    "type": "manual_trigger",
                    "position": {"x": 100.0, "y": 100.0},
                    "data": {
                        "label": "Start",
                        "type": "manual_trigger",
                        "config": {
                            "trigger_data": {
                                "test": "auto-create test workflow",
                                "timestamp": datetime.now().isoformat()
                            }
                        }
                    }
                },
                {
                    "id": "write-1",
                    "type": "google_sheets_write",
                    "position": {"x": 400.0, "y": 100.0},
                    "data": {
                        "label": "Write to Test Sheet",
                        "type": "google_sheets_write",
                        "config": {
                            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                            "sheet_name": "Test",  # Use Test sheet
                            "range": "A2",  # Start from A2 (after headers)
                            "mode": "append",
                            "data_format": "auto"
                        }
                    }
                }
            ],
            "edges": [
                {
                    "id": "start-write",
                    "source": "start-1",
                    "target": "write-1",
                    "type": "default"
                }
            ]
        },
        "template_type": "custom",
        "category": "test"
    }
    
    # Create template first
    template_request = {
        "name": f"Test Sheet Template - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Template for Test sheet auto-create",
        "template_data": workflow_data["template_data"],
        "template_type": "custom",
        "category": "test"
    }
    
    template_response = requests.post(
        "http://localhost:8000/api/v1/workflow/templates",
        json=template_request
    )
    
    if template_response.status_code == 200:
        template_data = template_response.json()
        template_id = template_data['template']['id']
        print(f"✅ Template created: {template_id}")
        
        # Create instance from template
        instance_data = {
            "name": f"Test Sheet Instance - {datetime.now().strftime('%H:%M:%S')}",
            "template_id": template_id,
            "data": workflow_data["template_data"]
        }
        
        instance_response = requests.post(
            "http://localhost:8000/api/v1/workflow/instances",
            json=instance_data
        )
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data['instance']['id']
            print(f"✅ Instance created: {instance_id}")
            
            # Execute workflow
            print("\n📤 Executing workflow...")
            execute_response = requests.post(f"http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute")
            
            if execute_response.status_code == 200:
                result = execute_response.json()
                print(f"✅ Workflow executed!")
                print(f"📊 Result: {result}")
                return instance_id
            else:
                print(f"❌ Failed to execute: {execute_response.status_code}")
                print(f"Error: {execute_response.text}")
        else:
            print(f"❌ Failed to create instance: {instance_response.status_code}")
            print(f"Error: {instance_response.text}")
    else:
        print(f"❌ Failed to create template: {template_response.status_code}")
        print(f"Error: {template_response.text}")
    
    return None

if __name__ == "__main__":
    instance_id = main()
    if instance_id:
        print(f"\n🔗 Instance ID: {instance_id}")
        print("Wait 5 seconds then check the Test sheet for data...")
        import time
        time.sleep(5)
        
        # Check Test sheet
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from services.google_sheets_service import GoogleSheetsService
        
        service = GoogleSheetsService()
        if service.authenticate():
            sheet_id = '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc'
            data = service.read_sheet(sheet_id, 'Test!A1:D10')
            print(f'\n📊 Data in Test sheet ({len(data) if data else 0} rows):')
            if data:
                for i, row in enumerate(data):
                    print(f'  Row {i+1}: {row}')
            else:
                print("  No data found")
