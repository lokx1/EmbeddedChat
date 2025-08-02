#!/usr/bin/env python3
"""
Test why GoogleSheetsWrite is falling back to simulation
"""

import requests
import json
from datetime import datetime

def test_why_simulation():
    """Test why GoogleSheetsWrite uses simulation instead of real API"""
    
    # Get the Sheet ID from frontend config
    frontend_sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    print(f"🔍 Debugging why simulation mode is used")
    print(f"📊 Target Sheet ID: {frontend_sheet_id}")
    
    # Test direct GoogleSheetsService authentication
    print("\\n1️⃣ Testing GoogleSheetsService directly...")
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.services.workflow.google_services import GoogleSheetsService
        import asyncio
        
        async def test_direct_api():
            service = GoogleSheetsService()
            
            print("   🔐 Authenticating...")
            auth_result = await service.authenticate()
            print(f"   Authentication: {'✅ SUCCESS' if auth_result else '❌ FAILED'}")
            
            if auth_result:
                print("   📝 Testing write operation...")
                success, result = await service.write_to_sheet(
                    sheet_id=frontend_sheet_id,
                    sheet_name="DirectAPITest",
                    range_start="A1",
                    mode="overwrite",
                    data=[
                        ["Direct API Test", "Status", "Timestamp"],
                        ["GoogleSheetsService", "SUCCESS", datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                    ]
                )
                
                print(f"   Write result: {'✅ SUCCESS' if success else '❌ FAILED'}")
                if success:
                    print(f"   Operation: {result.get('operation', 'N/A')}")
                    print(f"   Status: {result.get('status', 'N/A')}")
                else:
                    print(f"   Error: {result.get('error', 'N/A')}")
                    
                return success
            return False
        
        direct_success = asyncio.run(test_direct_api())
        
    except Exception as e:
        print(f"   ❌ Direct API test failed: {e}")
        direct_success = False
    
    # Test workflow execution with correct Sheet ID
    print("\\n2️⃣ Testing workflow with correct Sheet ID...")
    
    workflow_data = {
        "nodes": [
            {
                "id": "trigger-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Manual Trigger",
                    "type": "manual_trigger",
                    "config": {}
                }
            },
            {
                "id": "sheets-write-1",
                "type": "google_sheets_write",
                "position": {"x": 400, "y": 100},
                "data": {
                    "label": "Debug Write Test",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": frontend_sheet_id,  # Use correct Sheet ID
                        "sheet_name": f"DebugTest_{datetime.now().strftime('%H%M%S')}",
                        "range": "A1",
                        "mode": "overwrite",
                        "data_format": "auto"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "trigger-1",
                "target": "sheets-write-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    base_url = "http://localhost:8000/api/v1"
    
    # Save workflow
    save_payload = {
        "name": f"Debug Simulation Test - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Debug why simulation mode is used",
        "workflow_data": workflow_data,
        "category": "debug"
    }
    
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"   ✅ Template created: {template_id}")
        
        # Create instance with explicit data
        instance_payload = {
            "template_id": template_id,
            "name": f"Debug Test - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": {
                "data": [
                    ["Debug Test", "Real API", "Check"],
                    [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "GoogleSheetsWrite", "SUCCESS"],
                    ["Should use real API", "Not simulation", "VERIFY"]
                ]
            }
        }
        
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            print(f"   ✅ Instance created: {instance_id}")
            
            # Execute
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            if execute_response.status_code == 200:
                print("   🚀 Execution started...")
                
                import time
                time.sleep(3)
                
                # Check result
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                if status_response.status_code == 200:
                    instance = status_response.json()["data"]["instance"]
                    
                    if instance.get('output_data') and 'node_outputs' in instance['output_data']:
                        write_output = instance['output_data']['node_outputs'].get('sheets-write-1', {})
                        operation = write_output.get('operation', 'N/A')
                        status = write_output.get('status', 'N/A')
                        
                        print(f"   📊 Workflow Result:")
                        print(f"      Operation: {operation}")
                        print(f"      Status: {status}")
                        
                        if status == 'success':
                            print("   🎉 SUCCESS! Real API was used!")
                            return True
                        elif status == 'simulated':
                            print("   ⚠️  Still simulation mode")
                            
                            # Get detailed logs to see why
                            logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                            if logs_response.status_code == 200:
                                steps = logs_response.json()["data"]["steps"]
                                for step in steps:
                                    if step['step_type'] == 'google_sheets_write':
                                        if step.get('error_message'):
                                            print(f"      ❌ Error causing fallback: {step['error_message']}")
                            return False
                        
    print("\\n🔍 Summary:")
    print(f"   Direct API test: {'✅ SUCCESS' if direct_success else '❌ FAILED'}")
    print("   Workflow test: Check above results")
    
    if not direct_success:
        print("\\n💡 Possible issues:")
        print("   - Google Sheets API credentials not working")
        print("   - Authentication failing in workflow context")
        print("   - Import/module issues")
    
    return direct_success

if __name__ == "__main__":
    print("=== Debug Simulation Mode ===\\n")
    test_why_simulation()
