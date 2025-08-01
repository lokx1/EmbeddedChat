#!/usr/bin/env python3
"""
Create a complete demo workflow instance for AI Asset Generation
"""

import requests
import json
from datetime import datetime

def create_demo_workflow():
    """Create a demo workflow for AI asset generation"""
    print("🎨 Creating Demo AI Asset Generation Workflow")
    print("="*50)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Workflow data matching React Flow format
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
                        "provider": "openai",
                        "model": "gpt-4o",
                        "prompt": "Based on this asset request: {input}\n\nGenerate a comprehensive asset specification including:\n1. Technical details\n2. Style guidelines\n3. Implementation notes\n4. Quality requirements\n\nConsider the output format and create appropriate content recommendations.",
                        "temperature": 0.7,
                        "max_tokens": 1000
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
    
    # Create workflow instance
    workflow_payload = {
        "name": "AI Asset Generation Pipeline",
        "description": "Automated pipeline to read asset specifications from Google Sheets, process them with AI, and write results back",
        "category": "AI Processing",
        "workflow_data": workflow_data,
        "is_public": True
    }
    
    try:
        # Save workflow
        print("💾 Saving workflow...")
        save_url = f"{base_url}/editor/save"
        
        response = requests.post(
            save_url,
            json=workflow_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            workflow_id = result.get("data", {}).get("workflow_id")
            
            print(f"✅ Workflow saved successfully!")
            print(f"📋 Workflow ID: {workflow_id}")
            print(f"🎨 Name: {workflow_payload['name']}")
            print(f"📄 Description: {workflow_payload['description']}")
            print(f"🔧 Components: {len(workflow_data['nodes'])}")
            print(f"🔗 Connections: {len(workflow_data['edges'])}")
            
            # Create workflow instance for execution
            print(f"\n🚀 Creating workflow instance...")
            instance_payload = {
                "name": f"AI Asset Generation - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "template_id": workflow_id,
                "workflow_data": workflow_data,  # Include the workflow data
                "input_data": {},
                "created_by": "demo_user"
            }
            
            instance_response = requests.post(
                f"{base_url}/instances",
                json=instance_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if instance_response.status_code == 200:
                instance_result = instance_response.json()
                print(f"Debug - Instance response: {instance_result}")  # Debug line
                instance_id = instance_result.get("instance_id") or instance_result.get("data", {}).get("instance_id")
                
                if instance_id:
                    print(f"✅ Workflow instance created!")
                    print(f"🆔 Instance ID: {instance_id}")
                else:
                    print(f"⚠️  Instance created but ID not found in response")
                    print(f"Response: {instance_result}")
                
                # Show frontend URLs
                print(f"\n🖥️  Frontend Testing URLs:")
                print(f"   Editor: http://localhost:3000/workflow/editor/{workflow_id}")
                print(f"   Dashboard: http://localhost:3000/workflow/dashboard")
                print(f"   Instance: http://localhost:3000/workflow/instances/{instance_id}")
                
                # Show Google Sheets URLs
                print(f"\n📊 Google Sheets URLs:")
                sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
                print(f"   Input Data: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0")
                print(f"   Results: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=1")
                
                # Show component configuration
                print(f"\n⚙️  Component Configuration:")
                for i, node in enumerate(workflow_data['nodes'], 1):
                    config = node['data'].get('config', {})
                    print(f"   {i}. {node['data']['label']} ({node['type']})")
                    if config:
                        for key, value in list(config.items())[:2]:  # Show first 2 config items
                            print(f"      {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                
                return {
                    "workflow_id": workflow_id,
                    "instance_id": instance_id,
                    "workflow_data": workflow_data
                }
            else:
                print(f"❌ Failed to create instance: {instance_response.status_code}")
                print(instance_response.text)
                return None
        else:
            print(f"❌ Failed to save workflow: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error creating workflow: {str(e)}")
        return None

def test_workflow_execution(workflow_info):
    """Test executing the workflow"""
    if not workflow_info:
        return False
    
    print(f"\n🎯 Testing Workflow Execution")
    print("="*35)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    instance_id = workflow_info["instance_id"]
    
    try:
        # Execute workflow
        print(f"▶️  Executing workflow instance: {instance_id}")
        
        execute_url = f"{base_url}/instances/{instance_id}/execute"
        response = requests.post(execute_url)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Workflow execution started!")
            print(f"📊 Status: {result.get('status', 'unknown')}")
            
            # Check execution status
            import time
            print(f"⏳ Checking execution status...")
            
            for i in range(10):  # Check for 10 seconds
                status_response = requests.get(f"{base_url}/instances/{instance_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data.get("data", {}).get("instance", {})
                    status = instance.get("status", "unknown")
                    
                    print(f"   Status: {status}")
                    
                    if status in ["completed", "failed"]:
                        break
                
                time.sleep(1)
            
            print(f"✅ Execution monitoring completed")
            return True
        else:
            print(f"❌ Failed to execute workflow: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Execution error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 AI Asset Generation Workflow Demo Setup")
    print("="*55)
    
    # Create demo workflow
    workflow_info = create_demo_workflow()
    
    if workflow_info:
        # Test execution
        execution_success = test_workflow_execution(workflow_info)
        
        print(f"\n🎉 DEMO SETUP COMPLETE!")
        print(f"✅ Workflow created and saved")
        print(f"✅ Instance ready for execution")
        if execution_success:
            print(f"✅ Test execution successful")
        
        print(f"\n🎨 Next Steps:")
        print(f"   1. Open frontend: http://localhost:3000")
        print(f"   2. Navigate to workflow editor")
        print(f"   3. Test the AI Asset Generation pipeline")
        print(f"   4. Check results in Google Sheets")
        
    else:
        print(f"\n❌ Demo setup failed")
        print(f"💡 Check backend connectivity and try again")
