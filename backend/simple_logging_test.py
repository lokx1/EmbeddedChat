"""
Simple test for enhanced logging - create workflow and execute via API
"""
import asyncio
import aiohttp
import json

async def test_workflow_with_logging():
    """Create and execute a workflow to test enhanced logging"""
    
    workflow_config = {
        "nodes": [
            {
                "id": "ai_node",
                "type": "ai_processing", 
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "AI Test for Logging",
                    "config": {
                        "model": "qwen2.5:3b",
                        "prompt": "Say hello world",
                        "temperature": 0.7
                    }
                }
            },
            {
                "id": "sheets_node",
                "type": "google_sheets_write",
                "position": {"x": 300, "y": 100}, 
                "data": {
                    "label": "Write to Test Sheet",
                    "config": {
                        "spreadsheet_id": "1BvELTeiQiAu--T-5OUnqRMQ0MS1JaKlCvSTR9TrAOe0",
                        "range": "Test!A1:D10",
                        "sheet_name": "Test"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "ai_to_sheets",
                "source": "ai_node", 
                "target": "sheets_node",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🚀 Creating workflow instance...")
            
            # Create workflow instance
            async with session.post(
                'http://localhost:8000/api/v1/workflow/instances',
                json={
                    "name": "Enhanced Logging Test",
                    "workflow_data": workflow_config
                }
            ) as response:
                if response.status == 200:
                    instance_data = await response.json()
                    instance_id = instance_data["id"]
                    print(f"✅ Created workflow instance: {instance_id}")
                    
                    # Execute workflow
                    print("⚡ Executing workflow...")
                    async with session.post(
                        f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute',
                        json={"input_data": {"test_message": "Enhanced logging test"}}
                    ) as exec_response:
                        if exec_response.status == 200:
                            exec_data = await exec_response.json()
                            print(f"✅ Workflow executed successfully")
                            print(f"Result: {exec_data}")
                            
                            # Wait for execution to complete
                            await asyncio.sleep(3)
                            
                            # Check the instance details
                            async with session.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}') as detail_response:
                                if detail_response.status == 200:
                                    detail_data = await detail_response.json()
                                    print(f"📊 Instance status: {detail_data.get('status')}")
                                    print(f"📊 Execution logs: {len(detail_data.get('execution_logs', []))} entries")
                                    
                                    return instance_id
                                    
                        else:
                            print(f"❌ Workflow execution failed: {exec_response.status}")
                            error_text = await exec_response.text()
                            print(f"Error: {error_text}")
                else:
                    print(f"❌ Failed to create workflow: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None


async def check_database_logs():
    """Check if logs were written to database"""
    import sys
    sys.path.append('src')
    
    from models.database import AsyncSessionLocal
    from models.workflow import WorkflowTaskLog, WorkflowExecutionStep
    from sqlalchemy import select
    
    try:
        async with AsyncSessionLocal() as db:
            # Check task logs
            task_logs_result = await db.execute(select(WorkflowTaskLog).order_by(WorkflowTaskLog.created_at.desc()).limit(5))
            task_logs = task_logs_result.scalars().all()
            
            print(f"📊 Found {len(task_logs)} task logs in database:")
            for log in task_logs:
                print(f"  - {log.task_name} ({log.task_type}): {log.status}")
                if log.failure_reason:
                    print(f"    Error: {log.failure_reason}")
                if log.processing_time_ms:
                    print(f"    Processing time: {log.processing_time_ms}ms")
            
            # Check execution steps
            steps_result = await db.execute(select(WorkflowExecutionStep).order_by(WorkflowExecutionStep.created_at.desc()).limit(5))
            execution_steps = steps_result.scalars().all()
            
            print(f"📊 Found {len(execution_steps)} execution steps in database:")
            for step in execution_steps:
                print(f"  - {step.step_name} ({step.step_type}): {step.status}")
                if step.error_message:
                    print(f"    Error: {step.error_message}")
                if step.execution_time_ms:
                    print(f"    Execution time: {step.execution_time_ms}ms")
                    
    except Exception as e:
        print(f"❌ Error checking database logs: {e}")


async def main():
    print("🧪 Testing Enhanced Workflow Logging")
    print("=" * 40)
    
    # Test workflow execution
    instance_id = await test_workflow_with_logging()
    
    if instance_id:
        print("\n📊 Checking database logs...")
        await check_database_logs()
    
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    asyncio.run(main())
