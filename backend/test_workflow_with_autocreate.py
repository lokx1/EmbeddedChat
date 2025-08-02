#!/usr/bin/env python3
"""Test workflow execution with auto-created sheet"""

import asyncio
import sys
import os
import requests
from datetime import datetime
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.google_sheets_service import GoogleSheetsService

def main():
    print("🚀 Testing Workflow Execution with Auto-Created Sheet")
    print("=" * 50)
    
    # Get latest workflow instance
    try:
        response = requests.get("http://localhost:8000/api/v1/workflow/instances")
        if response.status_code == 200:
            instances = response.json()
            if instances:
                latest_instance = instances[-1]
                instance_id = latest_instance['id']
                print(f"📋 Using instance ID: {instance_id}")
                print(f"📝 Instance name: {latest_instance.get('name', 'Unknown')}")
                
                # Check workflow configuration
                if 'data' in latest_instance and 'nodes' in latest_instance['data']:
                    nodes = latest_instance['data']['nodes']
                    google_sheets_nodes = [node for node in nodes if node.get('type') == 'GoogleSheetsWrite']
                    if google_sheets_nodes:
                        config = google_sheets_nodes[0].get('data', {}).get('config', {})
                        print(f"📊 Sheet config: {config}")
                
                # Execute workflow
                print("\n📤 Executing workflow...")
                execute_response = requests.post(f"http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute")
                if execute_response.status_code == 200:
                    result = execute_response.json()
                    print(f"✅ Workflow executed!")
                    print(f"📊 Result: {result}")
                    
                    # Wait for async processing
                    print("\n⏳ Waiting for background processing...")
                    time.sleep(5)
                    
                    # Check sheet data
                    check_sheet_data()
                    
                else:
                    print(f"❌ Failed to execute workflow: {execute_response.status_code}")
                    print(f"Error: {execute_response.text}")
            else:
                print("❌ No workflow instances found")
        else:
            print(f"❌ Failed to get instances: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_sheet_data():
    """Check if data was written to the sheet"""
    print("\n=== Checking Sheet Data ===")
    
    service = GoogleSheetsService()
    
    if not service.authenticate():
        print("❌ Failed to authenticate")
        return
    
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    try:
        # Read from Test sheet
        data = service.read_sheet(sheet_id, "Test!A1:D10")
        if data:
            print(f"📊 Data in Test sheet ({len(data)} rows):")
            for i, row in enumerate(data):
                print(f"  Row {i+1}: {row}")
        else:
            print("📋 No data found in Test sheet")
            
        # Also check Result_Test sheet for comparison
        result_data = service.read_sheet(sheet_id, "Result_Test!A1:D10")
        if result_data:
            print(f"\n📊 Data in Result_Test sheet ({len(result_data)} rows):")
            for i, row in enumerate(result_data):
                print(f"  Row {i+1}: {row}")
        else:
            print("\n📋 No data found in Result_Test sheet")
            
    except Exception as e:
        print(f"❌ Error reading sheet: {e}")

if __name__ == "__main__":
    main()
