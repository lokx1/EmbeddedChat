#!/usr/bin/env python3
"""
Test AI Response Write with Fixed Credentials
"""

import requests
import json
from datetime import datetime

def test_ai_response_write_fixed():
    """Test workflow with fixed credentials path"""
    print("🔧 TESTING AI RESPONSE WRITE - FIXED CREDENTIALS")
    print("="*60)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Create simple test workflow
    workflow_data = {
        "nodes": [
            {
                "id": "trigger-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "config": {}
                }
            },
            {
                "id": "ai-1", 
                "type": "ai_processing",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "AI Processing",
                    "type": "ai_processing",
                    "config": {
                        "provider": "ollama",
                        "model": "qwen2.5:3b",
                        "prompt_template": "Generate asset specification for: {input}",
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                }
            },
            {
                "id": "sheets-write-1",
                "type": "google_sheets_write",
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "Write Results",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "AI_Test_Fixed",
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
                "target": "ai-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            },
            {
                "id": "edge-2", 
                "source": "ai-1",
                "target": "sheets-write-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # Sample input data
    input_data = {
        "records": [
            {
                "Description": "Design a Task Manager app logo",
                "Example Asset URL": "https://example.com/logo.png",
                "Desired Output Format": "PNG", 
                "Model Specification": "OpenAI"
            },
            {
                "Description": "Summer Sale banner",
                "Example Asset URL": "https://example.com/banner.jpg", 
                "Desired Output Format": "JPG",
                "Model Specification": "Claude"
            }
        ]
    }
    
    # 1. Save workflow template
    print("1️⃣ Creating workflow template...")
    save_payload = {
        "name": f"AI Response Test - Fixed - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Test AI response write with fixed credentials",
        "workflow_data": workflow_data,
        "category": "test"
    }
    
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    print(f"   Save response: {save_response.status_code}")
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"   ✅ Template created: {template_id}")
        
        # 2. Create workflow instance
        print("\n2️⃣ Creating workflow instance...")
        instance_payload = {
            "template_id": template_id,
            "name": f"AI Test Instance - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": input_data
        }
        
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        print(f"   Instance response: {instance_response.status_code}")
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            print(f"   ✅ Instance created: {instance_id}")
            
            # 3. Execute workflow
            print("\n3️⃣ Executing workflow...")
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            print(f"   Execute response: {execute_response.status_code}")
            
            if execute_response.status_code == 200:
                print("   ✅ Workflow execution started")
                
                # 4. Check status after execution
                import time
                print("\n4️⃣ Waiting for execution...")
                time.sleep(8)  # Wait longer for AI processing
                
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data["data"]["instance"]
                    
                    print(f"   📊 Final Status: {instance['status']}")
                    
                    if instance.get('output_data'):
                        output = instance['output_data']
                        print("   📤 Output Data Keys:", list(output.keys()))
                        
                        # Check for Google Sheets Write result
                        if 'node_outputs' in output and 'sheets-write-1' in output['node_outputs']:
                            sheets_output = output['node_outputs']['sheets-write-1']
                            print(f"\n   ✅ Google Sheets Write Result:")
                            print(f"      - Operation: {sheets_output.get('operation', 'N/A')}")
                            print(f"      - Status: {sheets_output.get('status', 'N/A')}")
                            print(f"      - Rows Written: {sheets_output.get('data_written', {}).get('rows_count', 'N/A')}")
                            
                            if sheets_output.get('status') == 'success':
                                print(f"\n   🎉 SUCCESS! Data written to Google Sheets!")
                                print(f"   📊 Check sheet: AI_Test_Fixed tab")
                                print(f"   ⭐ Look for Prompt column (F) with AI responses")
                                return True
                        
                        # Check AI processing result 
                        if 'node_outputs' in output and 'ai-1' in output['node_outputs']:
                            ai_output = output['node_outputs']['ai-1']
                            print(f"\n   🤖 AI Processing Result:")
                            print(f"      - Has results_for_sheets: {'results_for_sheets' in ai_output}")
                            if 'results_for_sheets' in ai_output:
                                results = ai_output['results_for_sheets']
                                print(f"      - Rows in results_for_sheets: {len(results)}")
                                if results and len(results) > 0:
                                    headers = results[0]
                                    print(f"      - Headers: {headers}")
                                    if "Prompt" in headers:
                                        print(f"      ⭐ Prompt column found at index {headers.index('Prompt')}")
                                    else:
                                        print(f"      ❌ Prompt column not found!")
                    
                    # Get logs for debugging
                    logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                    if logs_response.status_code == 200:
                        logs_data = logs_response.json()
                        steps = logs_data.get("data", {}).get("steps", [])
                        
                        print(f"\n   📋 Execution Logs ({len(steps)} steps):")
                        for step in steps:
                            if step['step_type'] in ['ai_processing', 'google_sheets_write']:
                                print(f"      [{step['step_type']}] {step['status']}")
                                if step.get('error_message'):
                                    print(f"         ❌ Error: {step['error_message']}")
                                if step.get('logs'):
                                    for log in step['logs'][-3:]:  # Show last 3 logs
                                        print(f"         📝 {log}")
                    
                    return instance['status'] == 'completed'
                else:
                    print(f"   ❌ Failed to get status: {status_response.text}")
            else:
                print(f"   ❌ Failed to execute: {execute_response.text}")
        else:
            print(f"   ❌ Failed to create instance: {instance_response.text}")
    else:
        print(f"   ❌ Failed to create template: {save_response.text}")
    
    return False

if __name__ == "__main__":
    success = test_ai_response_write_fixed()
    
    if success:
        print(f"\n🎉 TEST COMPLETED SUCCESSFULLY!")
        print(f"📊 Check your Google Sheets for new data in AI_Test_Fixed tab")
        print(f"⭐ Look for column F (Prompt) with cleaned AI responses")
    else:
        print(f"\n❌ TEST FAILED - Check logs above for details")
