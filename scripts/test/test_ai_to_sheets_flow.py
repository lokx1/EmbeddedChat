#!/usr/bin/env python3
"""
Test AI Processing to Sheets Write Data Flow
"""

import requests
import json
from datetime import datetime
import time

def test_ai_to_sheets_flow():
    """Test the complete AI Processing -> Google Sheets Write flow"""
    print("🔄 TESTING AI PROCESSING -> GOOGLE SHEETS WRITE FLOW")
    print("="*60)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Create workflow with AI Processing -> Google Sheets Write
    workflow_data = {
        "nodes": [
            {
                "id": "start-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "config": {}
                }
            },
            {
                "id": "sheets-read-1",
                "type": "google_sheets",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "Read Input Data",
                    "type": "google_sheets",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "TEST121",
                        "range": "A1:F100"
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
                        "provider": "ollama",
                        "model": "qwen2.5:3b",
                        "temperature": 0.7
                    }
                }
            },
            {
                "id": "sheets-write-1",
                "type": "google_sheets_write",
                "position": {"x": 700, "y": 100},
                "data": {
                    "label": "Write Results",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "AI_Results_Test",
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
                "source": "start-1",
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
                "target": "sheets-write-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    input_data = {}
    
    # Create workflow
    save_payload = {
        "name": f"AI -> Sheets Test - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Test AI Processing to Google Sheets Write flow",
        "workflow_data": workflow_data,
        "category": "ai_test"
    }
    
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"✅ Template created: {template_id}")
        
        # Create instance
        instance_payload = {
            "template_id": template_id,
            "name": f"AI Test Instance - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": input_data
        }
        
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            print(f"✅ Instance created: {instance_id}")
            
            # Execute
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            
            if execute_response.status_code == 200:
                print("✅ Execution started")
                
                # Wait for completion
                time.sleep(10)
                
                # Get detailed logs
                logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                if logs_response.status_code == 200:
                    logs_data = logs_response.json()
                    steps = logs_data.get("data", {}).get("steps", [])
                    
                    print(f"\n📊 EXECUTION STEPS ANALYSIS:")
                    
                    for step in steps:
                        print(f"\n🔸 STEP: {step['step_type']} - {step.get('step_name', 'Unknown')}")
                        print(f"   Status: {step['status']}")
                        
                        # Check AI Processing step
                        if step['step_type'] == 'ai_processing':
                            print(f"   📋 AI PROCESSING STEP:")
                            if step.get('output_data'):
                                output = step['output_data']
                                if 'results_for_sheets' in output:
                                    sheets_data = output['results_for_sheets']
                                    print(f"      ✅ results_for_sheets found: {len(sheets_data)} rows")
                                    if len(sheets_data) > 0:
                                        print(f"      📊 Headers: {sheets_data[0]}")
                                        if len(sheets_data) > 1:
                                            print(f"      📊 First data row: {sheets_data[1]}")
                                else:
                                    print(f"      ❌ No results_for_sheets in output")
                                    print(f"      Available keys: {list(output.keys())}")
                        
                        # Check Google Sheets Write step  
                        elif step['step_type'] == 'google_sheets_write':
                            print(f"   📝 GOOGLE SHEETS WRITE STEP:")
                            if step.get('logs'):
                                print(f"      📝 Detailed logs:")
                                for log in step['logs']:
                                    if "Found results_for_sheets" in log or "🎯" in log:
                                        print(f"         🎯 {log}")
                                    elif "Headers:" in log or "📊" in log:
                                        print(f"         📊 {log}")
                                    elif "results_for_sheets" in log:
                                        print(f"         📋 {log}")
                            
                            if step.get('output_data'):
                                output = step['output_data']
                                print(f"      📊 Operation: {output.get('operation', 'N/A')}")
                                print(f"      📊 Status: {output.get('status', 'N/A')}")
                                if output.get('status') == 'success':
                                    print(f"      ✅ SUCCESS! Rows written: {output.get('data_written', {}).get('rows_count', 'N/A')}")
                                    return True
                                elif output.get('status') == 'simulated':
                                    print(f"      ⚠️  Still in simulation mode!")
                
                # Get final status
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data["data"]["instance"]
                    print(f"\n📊 Final Status: {instance['status']}")
                    
                    if instance.get('output_data', {}).get('node_outputs'):
                        node_outputs = instance['output_data']['node_outputs']
                        
                        # Check AI Processing output
                        if 'ai-processing-1' in node_outputs:
                            ai_output = node_outputs['ai-processing-1']
                            if 'results_for_sheets' in ai_output:
                                print(f"✅ AI Processing created results_for_sheets: {len(ai_output['results_for_sheets'])} rows")
                            else:
                                print(f"❌ AI Processing missing results_for_sheets")
                        
                        # Check Sheets Write output
                        if 'sheets-write-1' in node_outputs:
                            sheets_output = node_outputs['sheets-write-1']
                            print(f"📊 Sheets Write Result: {sheets_output.get('status', 'N/A')}")
    
    return False

if __name__ == "__main__":
    success = test_ai_to_sheets_flow()
    
    if success:
        print(f"\n🎉 AI -> SHEETS FLOW WORKING!")
        print(f"📊 AI responses should now be in Google Sheets 'Prompt' column")
    else:
        print(f"\n❌ AI -> SHEETS FLOW ISSUE")
        print(f"💡 Check the data flow between AI Processing and Google Sheets Write")
