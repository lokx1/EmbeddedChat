#!/usr/bin/env python3
"""Create workflow instance directly with Test sheet name"""

import requests
import json
from datetime import datetime

def main():
    print("🚀 Creating workflow instance directly with 'Test' sheet name")
    
    # Create instance directly without template
    instance_data = {
        "name": f"Direct Test Sheet Instance - {datetime.now().strftime('%H:%M:%S')}",
        "template_id": None,
        "data": {
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
                                "test": "direct test workflow",
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
        "created_by": "test_autocreate"
    }
    
    instance_response = requests.post(
        "http://localhost:8000/api/v1/workflow/instances",
        json=instance_data
    )
    
    if instance_response.status_code == 200:
        instance_result = instance_response.json()
        instance_id = instance_result['instance']['id']
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
        else:
            print("❌ Failed to authenticate with Google Sheets")
