#!/usr/bin/env python3
"""
Create Workflow with Available Ollama Model
"""

import requests
import json
from datetime import datetime

def create_qwen_workflow():
    """Create a workflow using the available qwen3:8b model"""
    print("🚀 Creating Workflow with qwen3:8b")
    print("="*45)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Workflow with qwen3:8b model
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
                    "label": "AI Asset Generation (Qwen)",
                    "type": "ai_processing",
                    "config": {
                        "provider": "ollama",
                        "model": "qwen3:8b",  # Use available model
                        "prompt": "Based on this asset request: {input}\n\nGenerate a comprehensive asset specification including technical details and style guidelines.",
                        "temperature": 0.3,  # Lower temperature for stability
                        "max_tokens": 300    # Shorter response for faster processing
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
                        "sheet_name": "Qwen_Results",
                        "range": "A1",
                        "mode": "append",
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
        # Create workflow
        print("💾 Creating workflow with qwen3:8b...")
        
        workflow_payload = {
            "name": f"Qwen AI Workflow - {datetime.now().strftime('%H:%M:%S')}",
            "description": "Real Ollama integration using qwen3:8b model",
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
            return None
        
        workflow_result = save_response.json()
        workflow_id = workflow_result.get("data", {}).get("workflow_id")
        print(f"✅ Workflow created: {workflow_id}")
        
        return workflow_id
        
    except Exception as e:
        print(f"❌ Failed to create workflow: {str(e)}")
        return None

def execute_qwen_workflow(workflow_id):
    """Execute the qwen workflow"""
    print(f"\n🚀 Executing Qwen Workflow")
    print("="*35)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    try:
        # Create instance
        print("🔧 Creating instance...")
        
        # Get the workflow data first
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
                        "label": "AI Asset Generation (Qwen)",
                        "type": "ai_processing",
                        "config": {
                            "provider": "ollama",
                            "model": "qwen3:8b",
                            "prompt": "Based on this asset request: {input}\n\nGenerate a comprehensive asset specification including technical details and style guidelines.",
                            "temperature": 0.3,
                            "max_tokens": 300
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
                            "sheet_name": "Qwen_Results",
                            "range": "A1",
                            "mode": "append",
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

        instance_payload = {
            "name": f"Qwen Test - {datetime.now().strftime('%H:%M:%S')}",
            "template_id": workflow_id,
            "workflow_data": workflow_data,
            "input_data": {},
            "created_by": "qwen_test"
        }
        
        instance_response = requests.post(
            f"{base_url}/instances",
            json=instance_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if instance_response.status_code != 200:
            print(f"❌ Failed to create instance: {instance_response.status_code}")
            return False
        
        instance_result = instance_response.json()
        instance_id = instance_result.get("instance_id")
        print(f"✅ Instance created: {instance_id}")
        
        # Execute
        print("▶️  Executing workflow...")
        
        execute_response = requests.post(
            f"{base_url}/instances/{instance_id}/execute",
            headers={"Content-Type": "application/json"}
        )
        
        if execute_response.status_code != 200:
            print(f"❌ Failed to execute: {execute_response.status_code}")
            return False
        
        print(f"✅ Execution started!")
        print(f"🔗 Instance ID: {instance_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Execution failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 Qwen AI Workflow Test")
    print("="*30)
    
    # Create workflow
    workflow_id = create_qwen_workflow()
    
    if workflow_id:
        # Execute workflow
        success = execute_qwen_workflow(workflow_id)
        
        if success:
            print(f"\n🎉 QWEN WORKFLOW TEST COMPLETE!")
            print(f"✅ Workflow created with qwen3:8b model")
            print(f"✅ Execution started")
            print(f"🎯 Check backend logs for Ollama calls")
            print(f"📊 Check Qwen_Results sheet for outputs")
        else:
            print(f"\n❌ Execution failed")
    else:
        print(f"\n❌ Workflow creation failed")
