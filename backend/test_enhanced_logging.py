"""
Test the enhanced logging system with a real workflow execution
"""
import asyncio
import sys
import json
import uuid
from datetime import datetime

sys.path.append('src')

from src.models.database import get_db
from src.models.workflow import WorkflowInstance, WorkflowTaskLog, WorkflowExecutionStep
from src.services.workflow.execution_engine import WorkflowExecutionEngine


async def test_enhanced_logging():
    """Test the enhanced logging system"""
    
    # Get database session (async generator)
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        # Create a simple test workflow instance
        workflow_data = {
            "nodes": [
                {
                    "id": "input_1",
                    "type": "input",
                    "data": {
                        "label": "Input Node",
                        "config": {
                            "default_value": "Test input for logging"
                        }
                    },
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "ai_1", 
                    "type": "ai_processing",
                    "data": {
                        "label": "AI Processing",
                        "config": {
                            "model": "qwen3:8b",
                            "prompt": "Analyze this input and provide insights: {input}",
                            "max_tokens": 100
                        }
                    },
                    "position": {"x": 300, "y": 100}
                },
                {
                    "id": "sheets_1",
                    "type": "google_sheets_write", 
                    "data": {
                        "label": "Write to Sheets",
                        "config": {
                            "spreadsheet_id": "1TKRZqw5jvgPgaF6e1ZgvS8hbZvq8MEyI7o8YJMr-qkE",
                            "sheet_name": "Test_Logging",
                            "range": "A1:C10"
                        }
                    },
                    "position": {"x": 500, "y": 100}
                }
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "input_1",
                    "target": "ai_1",
                    "sourceHandle": "output",
                    "targetHandle": "input"
                },
                {
                    "id": "e2", 
                    "source": "ai_1",
                    "target": "sheets_1",
                    "sourceHandle": "output",
                    "targetHandle": "input"
                }
            ]
        }
        
        # Create workflow instance
        instance_id = str(uuid.uuid4())
        instance = WorkflowInstance(
            id=instance_id,
            name="Enhanced Logging Test",
            workflow_data=workflow_data,
            status="created",
            created_at=datetime.now()
        )
        
        db.add(instance)
        db.commit()
        
        print(f"Created test workflow instance: {instance_id}")
        
        # Execute workflow with logging
        execution_engine = WorkflowExecutionEngine(db)
        
        input_data = {
            "user_id": "test_user_123",
            "session_id": f"session_{datetime.now().timestamp()}",
            "input": "This is test data for the enhanced logging system"
        }
        
        print("Executing workflow with enhanced logging...")
        
        result = await execution_engine.execute_workflow(instance_id, input_data)
        
        print(f"Workflow execution completed with result: {result}")
        
        # Query the logs to verify they were created
        print("\n=== WORKFLOW EXECUTION STEPS ===")
        steps = db.query(WorkflowExecutionStep).filter(
            WorkflowExecutionStep.workflow_instance_id == instance_id
        ).order_by(WorkflowExecutionStep.created_at).all()
        
        for step in steps:
            print(f"Step: {step.step_name} ({step.step_type})")
            print(f"  Status: {step.status}")
            print(f"  Execution time: {step.execution_time_ms}ms")
            print(f"  Log level: {step.log_level}")
            print(f"  Component version: {step.component_version}")
            print(f"  User ID: {step.user_id}")
            print(f"  Tags: {step.tags}")
            print(f"  Metrics: {step.metrics}")
            print(f"  Dependencies: {step.dependencies}")
            print(f"  Artifacts: {step.artifacts}")
            if step.error_message:
                print(f"  Error: {step.error_message}")
            print()
        
        print("\n=== WORKFLOW TASK LOGS ===")
        task_logs = db.query(WorkflowTaskLog).filter(
            WorkflowTaskLog.workflow_instance_id == instance_id
        ).order_by(WorkflowTaskLog.created_at).all()
        
        for log in task_logs:
            print(f"Task: {log.task_name} ({log.task_type})")
            print(f"  Task ID: {log.task_id}")
            print(f"  Status: {log.status}")
            print(f"  Log level: {log.log_level}")
            print(f"  Processing time: {log.processing_time_ms}ms")
            print(f"  User ID: {log.user_id}")
            print(f"  Session ID: {log.session_id}")
            print(f"  Correlation ID: {log.correlation_id}")
            print(f"  Tags: {log.tags}")
            print(f"  Context: {log.context}")
            
            if log.failure_reason:
                print(f"  Failure reason: {log.failure_reason}")
                print(f"  Error code: {log.error_code}")
            
            if log.sheet_id:
                print(f"  Sheet ID: {log.sheet_id}")
                print(f"  API response code: {log.api_response_code}")
                print(f"  Row number: {log.row_number}")
            
            if log.api_endpoint:
                print(f"  API endpoint: {log.api_endpoint}")
                print(f"  API response code: {log.api_response_code}")
            
            print(f"  Started: {log.started_at}")
            print(f"  Completed: {log.completed_at}")
            print()
        
        # Test log summary
        print("\n=== LOG SUMMARY ===")
        total_logs = len(task_logs)
        successful_logs = len([log for log in task_logs if log.status == "success"])
        failed_logs = len([log for log in task_logs if log.status == "failed"])
        
        print(f"Total task logs: {total_logs}")
        print(f"Successful: {successful_logs}")
        print(f"Failed: {failed_logs}")
        print(f"Success rate: {(successful_logs / total_logs * 100):.1f}%" if total_logs > 0 else "N/A")
        
        if task_logs:
            avg_execution_time = sum(log.processing_time_ms or 0 for log in task_logs) / len(task_logs)
            print(f"Average execution time: {avg_execution_time:.1f}ms")
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await db.close()


if __name__ == "__main__":
    print("Testing Enhanced Logging System")
    print("=" * 50)
    
    success = asyncio.run(test_enhanced_logging())
    
    if success:
        print("\n✅ Enhanced logging test completed successfully!")
        print("Check the database for detailed task logs and execution steps.")
    else:
        print("\n❌ Enhanced logging test failed.")
