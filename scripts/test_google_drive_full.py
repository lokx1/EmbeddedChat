#!/usr/bin/env python3
"""
Test Google Drive Write component with real folder
"""

import requests
import json
from datetime import datetime

def test_google_drive_write_workflow():
    """Test creating and executing a workflow with Google Drive Write component"""
    base_url = "http://localhost:8000/api/v1"
    
    # 1. Create a workflow that reads from Google Sheets and writes to Google Drive
    workflow_data = {
        "nodes": [
            {
                "id": "trigger-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Manual Trigger",
                    "type": "manual_trigger",
                    "config": {
                        "trigger_data": {"test": "data", "timestamp": str(datetime.now())}
                    }
                }
            },
            {
                "id": "sheets-read-1", 
                "type": "google_sheets",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "Google Sheets Read",
                    "type": "google_sheets",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",  # Working sheet
                        "sheet_name": "Sheet1",
                        "range": "A1:Z1000",
                        "operation": "read"
                    }
                }
            },
            {
                "id": "ai-processing-1",
                "type": "ai_processing", 
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "AI Processing",
                    "type": "ai_processing",
                    "config": {
                        "provider": "qwen",
                        "model": "qwen2.5:3b",
                        "prompt": "Analyze this data and create a summary report with insights and recommendations.",
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                }
            },
            {
                "id": "drive-write-1",
                "type": "google_drive_write",
                "position": {"x": 700, "y": 100},
                "data": {
                    "label": "Google Drive Write",
                    "type": "google_drive_write",
                    "config": {
                        "file_name": f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        "folder_id": "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182",  # Your Google Drive folder
                        "file_type": "json",
                        "content_source": "previous_output",
                        "mimetype": "application/json"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "trigger-1",
                "target": "sheets-read-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            },
            {
                "id": "edge-2", 
                "source": "sheets-read-1",
                "target": "ai-processing-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            },
            {
                "id": "edge-3",
                "source": "ai-processing-1", 
                "target": "drive-write-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # Save workflow template
    save_payload = {
        "name": "Sheets to Drive Processing",
        "description": "Read from Google Sheets, process with AI, save to Google Drive",
        "workflow_data": workflow_data,
        "category": "data_processing"
    }
    
    print("🚀 Creating workflow template...")
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    print(f"Save response: {save_response.status_code}")
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"✅ Template created with ID: {template_id}")
        
        # 2. Create workflow instance from template
        print("\n📊 Creating workflow instance...")
        instance_payload = {
            "template_id": template_id,
            "name": f"Sheets to Drive execution {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": {}
        }
        
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        print(f"Instance response: {instance_response.status_code}")
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            print(f"✅ Instance created with ID: {instance_id}")
            
            # 3. Execute the instance
            print("\n🚀 Executing workflow instance...")
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            print(f"Execute response: {execute_response.status_code}")
            
            if execute_response.status_code == 200:
                print(f"✅ Workflow execution started")
                
                # 4. Monitor execution status
                import time
                max_wait = 30  # Wait up to 30 seconds
                wait_time = 0
                
                while wait_time < max_wait:
                    time.sleep(2)
                    wait_time += 2
                    
                    status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        instance = status_data["data"]["instance"]
                        print(f"📋 Status: {instance['status']} (waited {wait_time}s)")
                        
                        if instance['status'] in ['completed', 'failed', 'error']:
                            break
                
                # Get final status
                final_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                if final_response.status_code == 200:
                    final_data = final_response.json()
                    instance = final_data["data"]["instance"]
                    
                    print(f"\n🏁 Final Status: {instance['status']}")
                    
                    if instance.get('output_data'):
                        print("📤 Output Data:")
                        print(json.dumps(instance['output_data'], indent=2))
                    
                    if instance.get('error_message'):
                        print(f"❌ Error: {instance['error_message']}")
                        
                    # Check workflow steps for detailed information
                    steps = instance.get('steps', [])
                    if steps:
                        print(f"\n📊 Workflow Steps ({len(steps)}):")
                        for i, step in enumerate(steps, 1):
                            print(f"\n  Step {i}: {step.get('node_type')} ({step.get('node_id')}) - {step.get('status')}")
                            
                            if step.get('logs'):
                                print("    📝 Logs:")
                                for log in step['logs']:
                                    print(f"      - {log}")
                            
                            if step.get('output_data'):
                                output = step['output_data']
                                if isinstance(output, dict):
                                    if step.get('node_type') == 'google_drive_write':
                                        print("    📁 Google Drive Upload Result:")
                                        if 'file_info' in output:
                                            file_info = output['file_info']
                                            print(f"      📄 File: {file_info.get('filename')}")
                                            print(f"      📁 Folder: {file_info.get('folder_id')}")
                                            print(f"      📊 Size: {file_info.get('size')} bytes")
                                            print(f"      🕒 Status: {output.get('status')}")
                                        if 'file_id' in output:
                                            print(f"      🔗 Drive File ID: {output['file_id']}")
                                            print(f"      🌐 Share Link: https://drive.google.com/file/d/{output['file_id']}/view")
                                    else:
                                        print(f"    📤 Output: {json.dumps(output, indent=6)}")
                                else:
                                    print(f"    📤 Output: {output}")
                            
                            if step.get('error_message'):
                                print(f"    ❌ Error: {step['error_message']}")
                                
                    return instance['status'] == 'completed'
            else:
                print(f"❌ Failed to execute workflow: {execute_response.text}")
                return False
        else:
            print(f"❌ Failed to create instance: {instance_response.text}")
            return False
    else:
        print(f"❌ Failed to create template: {save_response.text}")
        return False

def test_simple_drive_write():
    """Test simple Google Drive Write component"""
    base_url = "http://localhost:8000/api/v1"
    
    # Simple workflow with just trigger and drive write
    workflow_data = {
        "nodes": [
            {
                "id": "trigger-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Manual Trigger",
                    "type": "manual_trigger",
                    "config": {
                        "trigger_data": {
                            "sample_data": [
                                {"name": "John", "age": 30, "city": "New York"},
                                {"name": "Jane", "age": 25, "city": "San Francisco"}
                            ],
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                }
            },
            {
                "id": "drive-write-1",
                "type": "google_drive_write",
                "position": {"x": 400, "y": 100},
                "data": {
                    "label": "Google Drive Write",
                    "type": "google_drive_write",
                    "config": {
                        "file_name": f"simple_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        "folder_id": "14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182",
                        "file_type": "json",
                        "content_source": "previous_output"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "trigger-1",
                "target": "drive-write-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # Create and execute simple workflow
    save_payload = {
        "name": "Simple Drive Write Test",
        "description": "Simple test of Google Drive Write component",
        "workflow_data": workflow_data,
        "category": "test"
    }
    
    print("🚀 Creating simple Drive write workflow...")
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"✅ Template created with ID: {template_id}")
        
        # Create and execute instance
        instance_payload = {
            "template_id": template_id,
            "name": f"Simple Drive test {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": {}
        }
        
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            print(f"✅ Instance created with ID: {instance_id}")
            
            # Execute
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            if execute_response.status_code == 200:
                print(f"✅ Workflow execution started")
                
                # Wait and check result
                import time
                time.sleep(5)
                
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data["data"]["instance"]
                    
                    print(f"\n🏁 Final Status: {instance['status']}")
                    
                    steps = instance.get('steps', [])
                    for step in steps:
                        if step.get('node_type') == 'google_drive_write':
                            print(f"\n📁 Google Drive Write Result:")
                            print(f"   Status: {step.get('status')}")
                            if step.get('output_data'):
                                output = step['output_data']
                                if 'file_info' in output:
                                    file_info = output['file_info']
                                    print(f"   📄 File: {file_info.get('filename')}")
                                    print(f"   📁 Folder: {file_info.get('folder_id')}")
                                    print(f"   📊 Size: {file_info.get('size')} bytes")
                                if 'file_id' in output:
                                    print(f"   🔗 File ID: {output['file_id']}")
                                    print(f"   🌐 Link: https://drive.google.com/file/d/{output['file_id']}/view")
                            if step.get('logs'):
                                print(f"   📝 Logs: {step['logs']}")
                            if step.get('error_message'):
                                print(f"   ❌ Error: {step['error_message']}")
                                
                    return instance['status'] == 'completed'
    
    return False

def check_google_drive_component():
    """Check if Google Drive Write component is available"""
    print("🔍 Checking Google Drive Write component availability...")
    
    components_response = requests.get("http://localhost:8000/api/v1/workflow/components")
    if components_response.status_code == 200:
        components = components_response.json()["data"]
        
        drive_component = None
        for comp in components:
            if comp["type"] == "google_drive_write":
                drive_component = comp
                break
        
        if drive_component:
            print("✅ Google Drive Write component found!")
            print(f"   Name: {drive_component['name']}")
            print(f"   Description: {drive_component['description']}")
            print(f"   Category: {drive_component['category']}")
            print(f"   Parameters: {len(drive_component['parameters'])}")
            
            for param in drive_component['parameters']:
                required = "required" if param['required'] else "optional"
                default = f" (default: {param.get('default_value', 'none')})" if param.get('default_value') else ""
                print(f"     - {param['name']}: {param['type']} ({required}){default}")
            
            return True
        else:
            print("❌ Google Drive Write component not found")
            available_types = [comp["type"] for comp in components]
            print(f"Available components: {available_types}")
            return False
    else:
        print(f"❌ Failed to get components: {components_response.text}")
        return False

if __name__ == "__main__":
    print("=== Google Drive Write Component Test ===\n")
    
    # Test 1: Check component availability
    component_available = check_google_drive_component()
    
    if component_available:
        print("\n" + "="*50)
        print("🧪 Test 1: Simple Google Drive Write")
        print("="*50)
        simple_success = test_simple_drive_write()
        
        print("\n" + "="*50)
        print("🧪 Test 2: Full Pipeline (Sheets → AI → Drive)")
        print("="*50)
        pipeline_success = test_google_drive_write_workflow()
        
        if simple_success and pipeline_success:
            print("\n🎉 All tests passed! Files should be uploaded to your Google Drive folder.")
            print("📁 Check folder: https://drive.google.com/drive/folders/14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182")
        else:
            print(f"\n⚠️  Tests completed with some issues:")
            print(f"   Simple test: {'✅' if simple_success else '❌'}")
            print(f"   Pipeline test: {'✅' if pipeline_success else '❌'}")
    else:
        print("\n❌ Cannot run tests - Google Drive Write component not available")
