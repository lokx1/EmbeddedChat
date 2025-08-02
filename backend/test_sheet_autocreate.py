#!/usr/bin/env python3
"""Test script for auto-creating sheet functionality"""

import asyncio
import sys
import os
import requests
from datetime import datetime
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.google_sheets_service import GoogleSheetsService

def test_api_available():
    """Test if API is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_direct_sheet_creation():
    """Test direct sheet creation using GoogleSheetsService"""
    print("=== Testing Direct Sheet Creation ===")
    
    service = GoogleSheetsService()
    
    # Test authentication
    if not service.authenticate():
        print("❌ Failed to authenticate with Google Sheets API")
        return False
    
    print("✅ Authentication successful")
    
    # Test sheet ID
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    # Get sheet info
    sheet_info = service.get_sheet_info(sheet_id)
    if sheet_info:
        existing_sheets = [sheet['title'] for sheet in sheet_info.get('sheets', [])]
        print(f"📋 Existing sheets: {existing_sheets}")
        
        # Check if "Test" sheet exists
        if "Test" not in existing_sheets:
            print("📝 Creating 'Test' sheet...")
            create_success = service.create_sheet(sheet_id, "Test")
            if create_success:
                print("✅ Sheet 'Test' created successfully!")
                
                # Add headers
                headers = [["Name", "Value", "Timestamp", "Status"]]
                write_success = service.write_sheet(sheet_id, "Test!A1", headers)
                if write_success:
                    print("✅ Headers added to sheet")
                else:
                    print("❌ Failed to add headers")
            else:
                print("❌ Failed to create sheet 'Test'")
        else:
            print("✅ Sheet 'Test' already exists")
    else:
        print("❌ Failed to get sheet info")
        return False
    
    return True

def execute_workflow():
    """Execute the test workflow"""
    print("\n=== Executing Workflow ===")
    
    if not test_api_available():
        print("❌ API not available")
        return False
    
    # Get the latest workflow instance
    try:
        response = requests.get("http://localhost:8000/api/v1/workflow/instances")
        if response.status_code == 200:
            instances = response.json()
            if instances:
                latest_instance = instances[-1]
                instance_id = latest_instance['id']
                print(f"📋 Using instance ID: {instance_id}")
                
                # Execute workflow
                execute_response = requests.post(f"http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute")
                if execute_response.status_code == 200:
                    result = execute_response.json()
                    print(f"✅ Workflow executed successfully!")
                    print(f"📊 Result: {result}")
                    return True
                else:
                    print(f"❌ Failed to execute workflow: {execute_response.status_code}")
                    print(f"Error: {execute_response.text}")
            else:
                print("❌ No workflow instances found")
        else:
            print(f"❌ Failed to get instances: {response.status_code}")
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")
    
    return False

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
            print(f"📊 Data in Test sheet:")
            for i, row in enumerate(data):
                print(f"  Row {i+1}: {row}")
        else:
            print("📋 No data found in Test sheet")
    except Exception as e:
        print(f"❌ Error reading sheet: {e}")

def main():
    """Main test function"""
    print("🚀 Testing Auto-Create Sheet Functionality")
    print("=" * 50)
    
    # Step 1: Test direct sheet creation
    sheet_created = test_direct_sheet_creation()
    
    # Wait a bit for API to be ready
    time.sleep(2)
    
    # Step 2: Execute workflow
    if sheet_created:
        workflow_executed = execute_workflow()
        
        # Step 3: Check if data was written
        if workflow_executed:
            time.sleep(3)  # Wait for async processing
            check_sheet_data()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()
