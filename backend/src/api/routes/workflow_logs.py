"""
API endpoints for workflow logging and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ...core.database import get_db
from ...models.workflow import WorkflowTaskLog, WorkflowExecutionStep, WorkflowInstance
from ...schemas.workflow_logs import (
    WorkflowTaskLogResponse, 
    WorkflowExecutionStepResponse,
    LogQueryParams,
    LogSummaryResponse
)

router = APIRouter(prefix="/workflow/logs", tags=["workflow-logs"])


@router.get("/tasks", response_model=List[WorkflowTaskLogResponse])
def get_task_logs(
    db: Session = Depends(get_db),
    workflow_instance_id: Optional[str] = Query(None, description="Filter by workflow instance ID"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    status: Optional[str] = Query(None, description="Filter by status (success, failed, processing)"),
    log_level: Optional[str] = Query(None, description="Filter by log level"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, description="Number of logs to return"),
    offset: int = Query(0, description="Offset for pagination"),
    start_date: Optional[datetime] = Query(None, description="Filter logs after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter logs before this date")
):
    """Get workflow task logs with filtering and pagination"""
    
    query = db.query(WorkflowTaskLog)
    
    # Apply filters
    if workflow_instance_id:
        query = query.filter(WorkflowTaskLog.workflow_instance_id == workflow_instance_id)
    
    if task_type:
        query = query.filter(WorkflowTaskLog.task_type == task_type)
    
    if status:
        query = query.filter(WorkflowTaskLog.status == status)
    
    if log_level:
        query = query.filter(WorkflowTaskLog.log_level == log_level)
    
    if user_id:
        query = query.filter(WorkflowTaskLog.user_id == user_id)
    
    if start_date:
        query = query.filter(WorkflowTaskLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(WorkflowTaskLog.created_at <= end_date)
    
    # Order by most recent first
    query = query.order_by(WorkflowTaskLog.created_at.desc())
    
    # Apply pagination
    logs = query.offset(offset).limit(limit).all()
    
    return [WorkflowTaskLogResponse.from_orm(log) for log in logs]


@router.get("/steps", response_model=List[WorkflowExecutionStepResponse])
def get_execution_steps(
    db: Session = Depends(get_db),
    workflow_instance_id: Optional[str] = Query(None, description="Filter by workflow instance ID"),
    step_type: Optional[str] = Query(None, description="Filter by step type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Number of steps to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """Get workflow execution steps with filtering and pagination"""
    
    query = db.query(WorkflowExecutionStep)
    
    # Apply filters
    if workflow_instance_id:
        query = query.filter(WorkflowExecutionStep.workflow_instance_id == workflow_instance_id)
    
    if step_type:
        query = query.filter(WorkflowExecutionStep.step_type == step_type)
    
    if status:
        query = query.filter(WorkflowExecutionStep.status == status)
    
    # Order by execution order
    query = query.order_by(WorkflowExecutionStep.created_at.desc())
    
    # Apply pagination
    steps = query.offset(offset).limit(limit).all()
    
    return [WorkflowExecutionStepResponse.from_orm(step) for step in steps]


@router.get("/summary", response_model=LogSummaryResponse)
def get_log_summary(
    db: Session = Depends(get_db),
    workflow_instance_id: Optional[str] = Query(None, description="Filter by workflow instance ID"),
    hours: int = Query(24, description="Number of hours to look back")
):
    """Get summary statistics for workflow logs"""
    
    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    
    # Base query with time filter
    task_query = db.query(WorkflowTaskLog).filter(
        WorkflowTaskLog.created_at >= start_time,
        WorkflowTaskLog.created_at <= end_time
    )
    
    if workflow_instance_id:
        task_query = task_query.filter(WorkflowTaskLog.workflow_instance_id == workflow_instance_id)
    
    # Count by status
    total_tasks = task_query.count()
    successful_tasks = task_query.filter(WorkflowTaskLog.status == "success").count()
    failed_tasks = task_query.filter(WorkflowTaskLog.status == "failed").count()
    processing_tasks = task_query.filter(WorkflowTaskLog.status == "processing").count()
    
    # Average execution time
    completed_tasks = task_query.filter(
        WorkflowTaskLog.processing_time_ms.isnot(None),
        WorkflowTaskLog.status.in_(["success", "failed"])
    ).all()
    
    avg_execution_time = 0
    if completed_tasks:
        avg_execution_time = sum(task.processing_time_ms or 0 for task in completed_tasks) / len(completed_tasks)
    
    # Most common error types
    error_query = task_query.filter(WorkflowTaskLog.status == "failed")
    error_counts = {}
    
    for task in error_query.all():
        error_code = task.error_code or "UNKNOWN_ERROR"
        error_counts[error_code] = error_counts.get(error_code, 0) + 1
    
    # Task type distribution
    type_counts = {}
    for task in task_query.all():
        task_type = task.task_type or "unknown"
        type_counts[task_type] = type_counts.get(task_type, 0) + 1
    
    return LogSummaryResponse(
        total_tasks=total_tasks,
        successful_tasks=successful_tasks,
        failed_tasks=failed_tasks,
        processing_tasks=processing_tasks,
        success_rate=round((successful_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
        average_execution_time_ms=round(avg_execution_time, 2),
        time_range_hours=hours,
        error_distribution=error_counts,
        task_type_distribution=type_counts
    )


@router.get("/instances/{instance_id}/detailed", response_model=Dict[str, Any])
def get_detailed_instance_logs(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed logs for a specific workflow instance"""
    
    # Get workflow instance
    instance = db.query(WorkflowInstance).filter(
        WorkflowInstance.id == instance_id
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
    
    # Get all execution steps
    steps = db.query(WorkflowExecutionStep).filter(
        WorkflowExecutionStep.workflow_instance_id == instance_id
    ).order_by(WorkflowExecutionStep.created_at).all()
    
    # Get all task logs
    task_logs = db.query(WorkflowTaskLog).filter(
        WorkflowTaskLog.workflow_instance_id == instance_id
    ).order_by(WorkflowTaskLog.created_at).all()
    
    # Calculate summary metrics
    total_execution_time = sum(step.execution_time_ms or 0 for step in steps)
    successful_steps = [step for step in steps if step.status == "completed"]
    failed_steps = [step for step in steps if step.status == "failed"]
    
    return {
        "instance": {
            "id": instance.id,
            "name": instance.name,
            "status": instance.status,
            "created_at": instance.created_at,
            "started_at": instance.started_at,
            "completed_at": instance.completed_at
        },
        "execution_summary": {
            "total_steps": len(steps),
            "successful_steps": len(successful_steps),
            "failed_steps": len(failed_steps),
            "total_execution_time_ms": total_execution_time,
            "success_rate": round((len(successful_steps) / len(steps) * 100) if steps else 0, 2)
        },
        "execution_steps": [
            {
                "id": step.id,
                "step_name": step.step_name,
                "step_type": step.step_type,
                "status": step.status,
                "execution_time_ms": step.execution_time_ms,
                "error_message": step.error_message,
                "input_data": step.input_data,
                "output_data": step.output_data,
                "started_at": step.started_at,
                "completed_at": step.completed_at
            }
            for step in steps
        ],
        "task_logs": [
            {
                "id": log.id,
                "task_name": log.task_name,
                "task_type": log.task_type,
                "status": log.status,
                "log_level": log.log_level,
                "processing_time_ms": log.processing_time_ms,
                "failure_reason": log.failure_reason,
                "error_code": log.error_code,
                "sheet_id": log.sheet_id,
                "api_response_code": log.api_response_code,
                "created_at": log.created_at,
                "completed_at": log.completed_at
            }
            for log in task_logs
        ]
    }


@router.delete("/cleanup")
def cleanup_old_logs(
    db: Session = Depends(get_db),
    days_old: int = Query(30, description="Delete logs older than this many days"),
    dry_run: bool = Query(True, description="Preview what would be deleted without actually deleting")
):
    """Clean up old workflow logs"""
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    # Find logs to delete
    old_task_logs = db.query(WorkflowTaskLog).filter(
        WorkflowTaskLog.created_at < cutoff_date
    )
    
    old_execution_steps = db.query(WorkflowExecutionStep).filter(
        WorkflowExecutionStep.created_at < cutoff_date
    )
    
    task_log_count = old_task_logs.count()
    execution_step_count = old_execution_steps.count()
    
    if dry_run:
        return {
            "dry_run": True,
            "would_delete": {
                "task_logs": task_log_count,
                "execution_steps": execution_step_count
            },
            "cutoff_date": cutoff_date
        }
    
    # Actually delete the logs
    old_task_logs.delete()
    old_execution_steps.delete()
    db.commit()
    
    return {
        "deleted": {
            "task_logs": task_log_count,
            "execution_steps": execution_step_count
        },
        "cutoff_date": cutoff_date
    }
