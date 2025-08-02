#!/usr/bin/env python3

import asyncio
import sys
import os
import json
import requests
from datetime import datetime

async def test_exact_frontend_workflow():
    """Test the exact frontend workflow configuration"""
    
    print("🧪 Testing Exact Frontend Workflow Configuration")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Create workflow with the EXACT configuration from the frontend screenshot
    print("📋 Creating workflow with frontend configuration...")
    
    workflow_data = {
        "nodes": [
            {
                "id": "start-1", 
                "type": "manual_trigger",
                "data": {
                    "label": "Start",
                    "config": {}
                },
                "position": {"x": 100, "y": 100}
            },
            {
                "id": "sheets-read-2",
                "type": "google_sheets_read",
                "data": {
                    "label": "Read Input Data",
                    "config": {
                        "sheet_id": "1WjySc8DxYoPJf3gJtyPXUJpRfdFza", 
                        "sheet_name": "Result_Test",
                        "range": "A1:B10"
                    }
                },
                "position": {"x": 300, "y": 100}
            },
            {
                "id": "ai-processing-3",
                "type": "ai_processing",
                "data": {
                    "label": "AI Processing",
                    "config": {
                        "provider": "ollama",
                        "model": "qwen3:8b",
                        "prompt": "Create detailed assets based on: {description}",
                        "temperature": 0.7,
                        "max_tokens": 150
                    }
                },
                "position": {"x": 500, "y": 100}
            },
            {
                "id": "sheets-write-4",
                "type": "google_sheets_write",
                "data": {
                    "label": "Write Results",
                    "config": {
                        "sheet_id": "1WjySc8DxYoPJf3gJtyPXUJpRfdFza",
                        "sheet_name": "Test",  # This matches the frontend
                        "range": "A1",
                        "mode": "append",
                        "data_format": "auto"
                    }
                },
                "position": {"x": 700, "y": 100}
            }
        ],
        "edges": [
            {
                "id": "e1",
                "source": "start-1",
                "target": "sheets-read-2",
                "sourceHandle": "trigger",
                "targetHandle": "input"
            },
            {
                "id": "e2", 
                "source": "sheets-read-2",
                "target": "ai-processing-3",
                "sourceHandle": "data",
                "targetHandle": "input"
            },
            {
                "id": "e3",
                "source": "ai-processing-3", 
                "target": "sheets-write-4",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ]
    }
    
    # Create workflow instance
    create_response = requests.post(
        f"{base_url}/api/v1/workflow/instances",
        json={
            "name": f"Fixed Data Flow Test - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data
        }
    )
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create workflow: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return
    
    instance_data = create_response.json()
    instance_id = instance_data["instance_id"]
    print(f"✅ Created instance: {instance_id}")
    
    # Execute workflow
    print(f"\n📋 Executing workflow...")
    
    execute_response = requests.post(
        f"{base_url}/api/v1/workflow/instances/{instance_id}/execute",
        json={"input_data": {}}
    )
    
    if execute_response.status_code != 200:
        print(f"❌ Failed to execute workflow: {execute_response.status_code}")
        print(f"Response: {execute_response.text}")
        return
    
    print(f"✅ Execution started")
    
    # Wait for completion and check results
    print(f"\n📋 Waiting for completion...")
    
    for i in range(30):
        await asyncio.sleep(1)
        
        # Check status
        status_response = requests.get(f"{base_url}/api/v1/workflow/instances/{instance_id}")
        if status_response.status_code == 200:
            instance = status_response.json()
            instance_data = instance.get("data", {}).get("instance", {})
            status = instance_data.get("status", "unknown")
            
            print(f"  Status: {status} ({i+1}s)")
            
            if status in ["completed", "failed", "cancelled"]:
                print(f"\n📊 Final Status: {status}")
                
                # Check the sheet to see if data was written
                print(f"\n📋 Checking Google Sheets for written data...")
                await check_google_sheets_data()
                
                # Check execution steps  
                print(f"\n📋 Checking execution steps...")
                await check_execution_logs(instance_id)
                break
        else:
            print(f"  Failed to get status: {status_response.status_code}")
    else:
        print(f"\n⏰ Timeout waiting for completion")


async def check_google_sheets_data():
    """Check if data was written to Google Sheets"""
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from services.google_sheets_service import GoogleSheetsService
        
        service = GoogleSheetsService()
        
        # Read from the "Test" sheet to see if data was written
        sheet_id = "1WjySc8DxYoPJf3gJtyPXUJpRfdFza"
        data = await service.read_sheet(sheet_id, "Test", "A1:Z10")
        
        if data and len(data) > 0:
            print(f"✅ Data found in Test sheet: {len(data)} rows")
            for i, row in enumerate(data[:3]):  # Show first 3 rows
                print(f"  Row {i+1}: {row}")
        else:
            print(f"❌ No data found in Test sheet")
            
        # Also check if the sheet exists
        sheet_info = await service.get_sheet_info(sheet_id)
        if sheet_info and 'sheets' in sheet_info:
            sheet_names = [s['properties']['title'] for s in sheet_info['sheets']]
            print(f"📋 Available sheets: {sheet_names}")
            if "Test" in sheet_names:
                print(f"✅ 'Test' sheet exists")
            else:
                print(f"❌ 'Test' sheet does not exist")
        
    except Exception as e:
        print(f"❌ Error checking Google Sheets: {e}")


async def check_execution_logs(instance_id):
    """Check execution logs from database"""
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from core.database import get_db
        from models.workflow import WorkflowExecutionStep
        from sqlalchemy.orm import Session
        
        db: Session = next(get_db())
        try:
            steps = db.query(WorkflowExecutionStep).filter(
                WorkflowExecutionStep.workflow_instance_id == instance_id
            ).order_by(WorkflowExecutionStep.created_at).all()
            
            print(f"📋 Execution Steps ({len(steps)}):")
            for step in steps:
                print(f"  {step.step_name} ({step.step_type}): {step.status}")
                if step.step_type == 'google_sheets_write':
                    print(f"    Input sheet_id: {step.input_data.get('sheet_id', 'N/A')}")
                    print(f"    Input sheet_name: {step.input_data.get('sheet_name', 'N/A')}")
                    print(f"    Error: {step.error_message or 'None'}")
                    if step.output_data:
                        print(f"    Output success: {step.output_data.get('success', 'N/A')}")
                        if 'rows_written' in step.output_data:
                            print(f"    Rows written: {step.output_data['rows_written']}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error checking execution logs: {e}")


if __name__ == "__main__":
    asyncio.run(test_exact_frontend_workflow())
