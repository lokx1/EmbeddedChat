#!/usr/bin/env python3
"""
Create a test workflow to debug frontend/backend communication
"""
import requests
import json
import time
from datetime import datetime

def create_debug_workflow():
    """Create a simple test workflow to debug execution"""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Simple workflow with correct sheet configuration
    workflow_data = {
        "nodes": [
            {
                "id": "start-node",
                "type": "manual_trigger", 
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "config": {
                        "trigger_data": {
                            "message": "Debug test",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                }
            },
            {
                "id": "write-node", 
                "type": "google_sheets_write",
                "position": {"x": 400, "y": 100},
                "data": {
                    "label": "Write Results", 
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "Test",  # Use frontend sheet name
                        "range": "A1",
                        "mode": "append", 
                        "data_format": "auto"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "connection",
                "source": "start-node",
                "target": "write-node", 
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    print("🧪 Creating DEBUG workflow...")
    
    # Create template
    template_payload = {
        "name": "DEBUG Frontend-Backend Test",
        "description": "Debug workflow to test frontend-backend communication",
        "workflow_data": workflow_data,
        "category": "debug"
    }
    
    template_response = requests.post(f"{base_url}/workflow/editor/save", json=template_payload)
    print(f"Template creation: {template_response.status_code}")
    
    if template_response.status_code == 200:
        template_data = template_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"✅ Template ID: {template_id}")
        
        # Create instance
        instance_payload = {
            "name": f"Debug Test {datetime.now().strftime('%H:%M:%S')}",
            "template_id": template_id,
            "workflow_data": workflow_data,
            "input_data": {
                "debug_data": [
                    ["Name", "Value", "Timestamp"],
                    ["Debug Test", "Frontend-Backend", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                ]
            }
        }
        
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        print(f"Instance creation: {instance_response.status_code}")
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            print(f"✅ Instance ID: {instance_id}")
            
            # Execute
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            print(f"Execution start: {execute_response.status_code}")
            
            if execute_response.status_code == 200:
                print("✅ Execution started!")
                
                # Monitor execution
                print("\n⏳ Monitoring execution...")
                for i in range(10):  # Check for 10 seconds
                    time.sleep(1)
                    
                    status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                    if status_response.status_code == 200:
                        instance = status_response.json()
                        status = instance.get("status", "unknown")
                        
                        print(f"  Check {i+1}: Status = {status}")
                        
                        if status == "completed":
                            print("✅ Execution completed!")
                            
                            # Check output
                            output_data = instance.get("output_data", {})
                            if output_data:
                                print(f"📊 Output nodes: {list(output_data.keys())}")
                                
                                for node_id, output in output_data.items():
                                    if isinstance(output, dict):
                                        node_status = output.get("status", "unknown")
                                        operation = output.get("operation", "unknown")
                                        print(f"  {node_id}: {node_status} ({operation})")
                                        
                                        if node_status == "success":
                                            data_written = output.get("data_written", {})
                                            print(f"    ✅ Data: {data_written}")
                                        elif node_status == "simulated":
                                            print(f"    ⚠️  SIMULATED - API issue!")
                            else:
                                print("❌ NO OUTPUT DATA - Component not executed!")
                                
                            break
                        elif status == "failed":
                            error = instance.get("error_message", "Unknown")
                            print(f"❌ Failed: {error}")
                            break
                        elif status == "running":
                            print("  🔄 Still running...")
                        elif status in ["draft", "created"]:
                            print(f"  ⏸️  Status: {status} - not executing")
                    else:
                        print(f"  ❌ Status check failed: {status_response.status_code}")
                
                return instance_id
            else:
                print(f"❌ Execution failed: {execute_response.text}")
        else:
            print(f"❌ Instance creation failed: {instance_response.text}")
    else:
        print(f"❌ Template creation failed: {template_response.text}")
        
    return None

def check_google_sheets():
    """Check Google Sheets directly"""
    print(f"\n📊 Checking Google Sheets directly...")
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.services.google_sheets_service import get_sheets_service
        
        sheets_service = get_sheets_service()
        if sheets_service.authenticate():
            sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
            
            # Check Test sheet (frontend config)
            try:
                test_data = sheets_service.read_sheet(sheet_id, "Test!A1:D10")
                print(f"✅ 'Test' sheet: {len(test_data) if test_data else 0} rows")
                if test_data and len(test_data) > 1:
                    print(f"   Latest rows: {test_data[-2:]}")
            except Exception as e:
                print(f"❌ 'Test' sheet error: {e}")
                
        else:
            print("❌ Sheets authentication failed")
            
    except Exception as e:
        print(f"❌ Sheets check error: {e}")

if __name__ == "__main__":
    print("🔧 DEBUG: Frontend-Backend Workflow Communication")
    print("=" * 60)
    
    instance_id = create_debug_workflow()
    check_google_sheets()
    
    print(f"\n🎯 SUMMARY:")
    if instance_id:
        print(f"✅ Debug workflow created and executed")
        print(f"📋 Instance ID: {instance_id}")
        print(f"🔗 Check sheets: https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit")
    else:
        print(f"❌ Debug workflow failed")
        
    print(f"\n💡 If no data appears in sheets:")
    print(f"   1. Component receives wrong data format")
    print(f"   2. Sheet name mismatch (Test vs Result_Test)")
    print(f"   3. API authentication issues")
    print(f"   4. Frontend not passing data correctly")
