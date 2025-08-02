"""
Simplified workflow logs API - for testing
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ...core.database import get_db
from ...models.workflow import WorkflowTaskLog, WorkflowExecutionStep

router = APIRouter(prefix="/workflow/logs", tags=["workflow-logs"])


@router.get("/tasks")
def get_task_logs_simple(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get workflow task logs - simplified version"""
    try:
        logs = db.query(WorkflowTaskLog).limit(limit).all()
        return [
            {
                "id": log.id,
                "task_id": log.task_id,
                "task_name": log.task_name,
                "status": log.status,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    except Exception as e:
        return {"error": str(e), "logs": []}


@router.get("/steps")
def get_execution_steps_simple(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get workflow execution steps - simplified version"""
    try:
        steps = db.query(WorkflowExecutionStep).limit(limit).all()
        return [
            {
                "id": step.id,
                "workflow_instance_id": step.workflow_instance_id,
                "step_name": step.step_name,
                "status": step.status,
                "created_at": step.created_at.isoformat() if step.created_at else None
            }
            for step in steps
        ]
    except Exception as e:
        return {"error": str(e), "steps": []}


@router.get("/summary")
def get_log_summary_simple(db: Session = Depends(get_db)):
    """Get logging summary - simplified version"""
    try:
        total_logs = db.query(WorkflowTaskLog).count()
        total_steps = db.query(WorkflowExecutionStep).count()
        
        return {
            "total_task_logs": total_logs,
            "total_execution_steps": total_steps,
            "status": "ok"
        }
    except Exception as e:
        return {"error": str(e), "total_task_logs": 0, "total_execution_steps": 0}
