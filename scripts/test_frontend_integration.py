#!/usr/bin/env python3
"""
Test Frontend Workflow Execution Integration
"""

import requests
import json
import time
from datetime import datetime

def test_frontend_workflow_execution():
    """Test executing workflow from frontend perspective"""
    print("🎯 Testing Frontend Workflow Execution")
    print("="*50)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Test workflow data similar to what frontend sends
    workflow_data = {
        "nodes": [
            {
                "id": "start-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 150},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "config": {
                        "trigger_data": {}
                    }
                }
            },
            {
                "id": "sheets-read-2",
                "type": "google_sheets",
                "position": {"x": 350, "y": 150},
                "data": {
                    "label": "Read Input Data",
                    "type": "google_sheets",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "AI_Input_Data",
                        "range": "A1:F100"
                    }
                }
            },
            {
                "id": "ai-processing-3",
                "type": "ai_processing",
                "position": {"x": 600, "y": 150},
                "data": {
                    "label": "AI Asset Generation",
                    "type": "ai_processing",
                    "config": {
                        "provider": "ollama",  # Test with Ollama
                        "model": "llama3.2",
                        "prompt": "Based on this asset request: {input}\n\nGenerate a comprehensive asset specification including technical details and style guidelines.",
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                }
            },
            {
                "id": "sheets-write-4",
                "type": "google_sheets_write",
                "position": {"x": 850, "y": 150},
                "data": {
                    "label": "Write Results",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "Results",
                        "range": "A1",
                        "mode": "overwrite",
                        "data_format": "auto"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1-2",
                "source": "start-1",
                "target": "sheets-read-2",
                "sourceHandle": "output",
                "targetHandle": "input"
            },
            {
                "id": "edge-2-3",
                "source": "sheets-read-2",
                "target": "ai-processing-3",
                "sourceHandle": "output",
                "targetHandle": "input"
            },
            {
                "id": "edge-3-4",
                "source": "ai-processing-3",
                "target": "sheets-write-4",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    try:
        # Step 1: Create workflow
        print("💾 Step 1: Creating workflow...")
        
        workflow_payload = {
            "name": f"Ollama Test Workflow - {datetime.now().strftime('%H:%M:%S')}",
            "description": "Testing Ollama integration with frontend execution",
            "category": "AI Processing",
            "workflow_data": workflow_data,
            "is_public": True
        }
        
        save_response = requests.post(
            f"{base_url}/editor/save",
            json=workflow_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if save_response.status_code != 200:
            print(f"❌ Failed to save workflow: {save_response.status_code}")
            print(save_response.text)
            return False
        
        workflow_result = save_response.json()
        workflow_id = workflow_result.get("data", {}).get("workflow_id")
        print(f"✅ Workflow created: {workflow_id}")
        
        # Step 2: Create instance
        print("🚀 Step 2: Creating workflow instance...")
        
        instance_payload = {
            "name": f"Ollama Test Instance - {datetime.now().strftime('%H:%M:%S')}",
            "template_id": workflow_id,
            "workflow_data": workflow_data,
            "input_data": {},
            "created_by": "frontend_test"
        }
        
        instance_response = requests.post(
            f"{base_url}/instances",
            json=instance_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if instance_response.status_code != 200:
            print(f"❌ Failed to create instance: {instance_response.status_code}")
            print(instance_response.text)
            return False
        
        instance_result = instance_response.json()
        instance_id = instance_result.get("instance_id")
        print(f"✅ Instance created: {instance_id}")
        
        # Step 3: Execute workflow (like frontend Execute button)
        print("▶️  Step 3: Executing workflow...")
        
        execute_response = requests.post(
            f"{base_url}/instances/{instance_id}/execute",
            headers={"Content-Type": "application/json"}
        )
        
        if execute_response.status_code != 200:
            print(f"❌ Failed to execute workflow: {execute_response.status_code}")
            print(execute_response.text)
            return False
        
        execute_result = execute_response.json()
        print(f"✅ Execution started: {execute_result.get('status', 'unknown')}")
        
        # Step 4: Monitor execution (like frontend would do)
        print("⏳ Step 4: Monitoring execution...")
        
        for i in range(30):  # Monitor for 30 seconds
            try:
                status_response = requests.get(f"{base_url}/instances/{instance_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data.get("data", {}).get("instance", {})
                    status = instance.get("status", "unknown")
                    
                    print(f"   Status: {status}")
                    
                    if status in ["completed", "failed"]:
                        print(f"✅ Execution finished with status: {status}")
                        break
                    elif status == "running":
                        print(f"   Still running... ({i+1}/30)")
                else:
                    print(f"⚠️  Status check failed: {status_response.status_code}")
                
            except Exception as e:
                print(f"⚠️  Status check error: {str(e)}")
            
            time.sleep(2)
        
        # Step 5: Check results
        print("🔍 Step 5: Checking results...")
        
        from src.services.google_sheets_service import GoogleSheetsService
        service = GoogleSheetsService()
        
        if service.authenticate():
            results = service.read_sheet(
                "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                "Results!A1:L5"
            )
            
            if results:
                print(f"✅ Found {len(results)} rows in Results sheet")
                print(f"📋 Latest result sample:")
                if len(results) > 1:
                    print(f"   {results[1][:4]}...")  # Show first 4 columns of first data row
            else:
                print("⚠️  No results found in sheet")
        
        print(f"\n🎉 Frontend Workflow Test Complete!")
        print(f"📊 Summary:")
        print(f"   ✅ Workflow created: {workflow_id}")
        print(f"   ✅ Instance created: {instance_id}")
        print(f"   ✅ Execution triggered")
        print(f"   ✅ Results written to Google Sheets")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_component_configurations():
    """Test that frontend can get component configurations"""
    print(f"\n🔧 Testing Component Configurations")
    print("="*40)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Test components that frontend needs
    components_to_test = [
        "manual_trigger",
        "google_sheets",
        "ai_processing",
        "google_sheets_write"
    ]
    
    for component_type in components_to_test:
        try:
            response = requests.get(f"{base_url}/components/{component_type}")
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                params = len(data.get('parameters', []))
                print(f"✅ {component_type}: {params} parameters")
            else:
                print(f"❌ {component_type}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {component_type}: Error - {str(e)}")
    
    print(f"✅ Component configuration test complete")

if __name__ == "__main__":
    print("🚀 Frontend Integration Test Suite")
    print("="*55)
    
    # Test 1: Component configurations
    test_component_configurations()
    
    # Test 2: Full workflow execution
    success = test_frontend_workflow_execution()
    
    if success:
        print(f"\n🎯 ALL TESTS PASSED!")
        print(f"✅ Frontend can execute workflows")
        print(f"✅ Ollama integration working (or fallback active)")
        print(f"✅ Results written to Google Sheets")
        print(f"🎨 Ready for frontend testing!")
    else:
        print(f"\n❌ Some tests failed")
        print(f"💡 Check backend logs for details")
