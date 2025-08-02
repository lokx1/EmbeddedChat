#!/usr/bin/env python3
"""Test database direct write for Test sheet workflow"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_session_maker
from models.workflow import WorkflowInstance
import json

async def create_test_workflow():
    """Create workflow instance in database directly"""
    
    workflow_data = {
        "nodes": [
            {
                "id": "start-1",
                "type": "manual_trigger",
                "position": {"x": 100.0, "y": 100.0},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "config": {
                        "trigger_data": {
                            "test": "database direct workflow",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                }
            },
            {
                "id": "write-1", 
                "type": "GoogleSheetsWrite",
                "position": {"x": 400.0, "y": 100.0},
                "data": {
                    "label": "Write to Test Sheet",
                    "type": "GoogleSheetsWrite",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "Test",
                        "range": "A2",
                        "mode": "append",
                        "data_format": "auto"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "start-write",
                "source": "start-1",
                "target": "write-1",
                "type": "default"
            }
        ]
    }
    
    async with async_session_maker() as session:
        # Create workflow instance
        instance = WorkflowInstance(
            name=f"DB Direct Test - {datetime.now().strftime('%H:%M:%S')}",
            template_id=None,
            data=workflow_data,
            status="draft",
            created_by="db_test"
        )
        
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        
        print(f"✅ Created workflow instance: {instance.id}")
        return str(instance.id)

async def main():
    print("🗄️  Creating workflow instance directly in database")
    
    try:
        instance_id = await create_test_workflow()
        
        # Now execute via API
        import requests
        print(f"\n📤 Executing workflow {instance_id} via API...")
        
        execute_response = requests.post(f"http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute")
        
        if execute_response.status_code == 200:
            result = execute_response.json()
            print(f"✅ Workflow executed!")
            print(f"📊 Result: {result}")
            
            # Wait and check
            import time
            time.sleep(5)
            
            # Check Test sheet
            from services.google_sheets_service import GoogleSheetsService
            service = GoogleSheetsService()
            if service.authenticate():
                data = service.read_sheet("1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc", "Test!A1:D10")
                print(f'\n📊 Data in Test sheet ({len(data) if data else 0} rows):')
                if data:
                    for i, row in enumerate(data):
                        print(f'  Row {i+1}: {row}')
                else:
                    print("  No data found")
        else:
            print(f"❌ Failed to execute: {execute_response.status_code}")
            print(f"Error: {execute_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
