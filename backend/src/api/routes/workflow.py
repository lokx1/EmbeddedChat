"""
Workflow API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from ...core.database import get_db
from ...models.workflow import WorkflowTemplate, WorkflowInstance, WorkflowExecutionStep, WorkflowTaskLog
from ...schemas.workflow_editor import SaveWorkflowRequest, UpdateWorkflowRequest, WorkflowEditorResponse, WorkflowEditorData
from ...schemas.workflow_components import WorkflowComponentMetadata, ComponentCategory
from ...services.workflow.workflow_engine import WorkflowExecutor
from ...services.workflow.execution_engine import WorkflowExecutionEngine
from ...services.workflow.component_registry import component_registry
from ...services.workflow.websocket_manager import websocket_manager, handle_websocket_connection, execution_event_callback
from ...services.workflow.google_services import GoogleServicesManager
from ...services.workflow.notifications import NotificationManager, EmailService, SlackService
from ...services.workflow.analytics import AnalyticsService
from ...services.workflow.ai_providers import AIProviderFactory
from ...services.workflow.email_report_service import (
    EmailReportService, 
    WorkflowExecutionSummary, 
    WorkflowAnalytics,
    create_execution_summary_from_data,
    process_execution_logs_for_report
)

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.get("/health")
async def workflow_health():
    """Health check for workflow service"""
    return {
        "success": True,
        "message": "Workflow service is healthy",
        "timestamp": datetime.now().isoformat()
    }


# Dependency to get workflow execution engine
async def get_execution_engine(db: Session = Depends(get_db)) -> WorkflowExecutionEngine:
    """Get workflow execution engine"""
    engine = WorkflowExecutionEngine(db)
    # Add WebSocket callback for real-time updates
    engine.add_event_callback(execution_event_callback)
    return engine


# Component Management Endpoints

@router.get("/components", response_model=Dict[str, Any])
async def get_workflow_components(
    category: Optional[ComponentCategory] = None
):
    """Get available workflow components"""
    try:
        if category:
            components = component_registry.get_components_by_category(category)
        else:
            components = component_registry.get_all_components()
        
        return {
            "success": True,
            "data": components
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/components/{component_type}", response_model=Dict[str, Any])
async def get_component_metadata(component_type: str):
    """Get metadata for a specific component type"""
    try:
        component_class = component_registry.get_component(component_type)
        return {
            "success": True,
            "data": component_class.get_metadata()
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# WebSocket endpoint for real-time execution updates
@router.websocket("/ws/{instance_id}")
async def websocket_endpoint(websocket: WebSocket, instance_id: str):
    """WebSocket endpoint for real-time workflow execution updates"""
    await handle_websocket_connection(websocket, instance_id)


def get_workflow_executor(db: Session) -> 'WorkflowExecutor':
    """Get workflow executor with all dependencies"""
    
    try:
        # Initialize services (these would be configured from environment variables)
        google_services = GoogleServicesManager("path/to/credentials.json")
        
        from ...core.config import settings
        email_service = EmailService(
            smtp_server=settings.SMTP_SERVER,
            smtp_port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_USE_TLS
        )
        
        slack_service = SlackService(
            bot_token="your-slack-bot-token",
            default_channel="#workflow-notifications"
        )
        
        notification_manager = NotificationManager(
            email_service=email_service,
            slack_service=slack_service
        )
        
        analytics_service = AnalyticsService(db)
        
        ai_config = {
            "openai": {"api_key": "your-openai-api-key"},
            "claude": {"api_key": "your-claude-api-key"},
            "ollama": {"base_url": "http://localhost:11434"}
        }
        
        return WorkflowExecutor(
            google_services=google_services,
            notification_manager=notification_manager,
            analytics_service=analytics_service,
            ai_config=ai_config
        )
    except Exception as e:
        # For development, return None if services can't be initialized
        print(f"Warning: Could not initialize workflow executor: {e}")
        return None


@router.post("/templates")
async def create_workflow_template(
    template_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create a new workflow template"""
    try:
        template = WorkflowTemplate(
            id=str(uuid.uuid4()),
            name=template_data["name"],
            description=template_data.get("description"),
            template_data=template_data["workflow_data"],  # Fixed: WorkflowTemplate uses template_data field
            category=template_data.get("category"),
            is_public=template_data.get("is_public", False),
            created_by=template_data.get("created_by")
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return {
            "success": True,
            "template_id": template.id,
            "message": "Workflow template created successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_workflow_templates(
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List workflow templates"""
    try:
        # For development, return mock data if no templates exist
        query = db.query(WorkflowTemplate)
        
        if category:
            query = query.filter(WorkflowTemplate.category == category)
        
        if is_public is not None:
            query = query.filter(WorkflowTemplate.is_public == is_public)
        
        templates = query.all()
        
        # If no templates exist, return empty array
        return {
            "success": True,
            "data": {
                "templates": [
                    {
                        "id": template.id,
                        "name": template.name,
                        "description": template.description,
                        "category": template.category,
                        "is_public": template.is_public,
                        "created_at": template.created_at.isoformat() if template.created_at else None
                    }
                    for template in templates
                ]
            }
        }
        
    except Exception as e:
        # Return empty array on error for development
        return {
            "success": True,
            "data": {
                "templates": []
            }
        }


@router.get("/templates/{template_id}")
async def get_workflow_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific workflow template"""
    try:
        template = db.query(WorkflowTemplate).filter(
            WorkflowTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "template": {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "template_data": template.template_data,
                "category": template.category,
                "is_public": template.is_public,
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "updated_at": template.updated_at.isoformat() if template.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/instances")
async def create_workflow_instance(
    instance_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create a new workflow instance"""
    try:
        # If template_id is provided, get workflow_data from template
        workflow_data = instance_data.get("workflow_data")
        if not workflow_data and instance_data.get("template_id"):
            template = db.query(WorkflowTemplate).filter(
                WorkflowTemplate.id == instance_data["template_id"]
            ).first()
            if template:
                workflow_data = template.template_data
            else:
                raise HTTPException(status_code=404, detail="Template not found")
        
        if not workflow_data:
            raise HTTPException(status_code=400, detail="workflow_data is required")
        
        instance = WorkflowInstance(
            id=str(uuid.uuid4()),
            name=instance_data["name"],
            template_id=instance_data.get("template_id"),
            workflow_data=workflow_data,
            input_data=instance_data.get("input_data"),
            created_by=instance_data.get("created_by"),
            status="draft"
        )
        
        db.add(instance)
        db.commit()
        db.refresh(instance)
        
        return {
            "success": True,
            "instance_id": instance.id,
            "message": "Workflow instance created successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances")
async def list_workflow_instances(
    status: Optional[str] = None,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    db: Session = Depends(get_db)
):
    """List workflow instances"""
    try:
        query = db.query(WorkflowInstance)
        
        if status:
            query = query.filter(WorkflowInstance.status == status)
        
        instances = query.order_by(WorkflowInstance.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "instances": [
                    {
                        "id": instance.id,
                        "name": instance.name,
                        "template_id": instance.template_id,
                        "status": instance.status,
                        "created_at": instance.created_at.isoformat() if instance.created_at else None,
                        "started_at": instance.started_at.isoformat() if instance.started_at else None,
                        "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
                        "created_by": instance.created_by
                    }
                    for instance in instances
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances/{instance_id}")
async def get_workflow_instance(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific workflow instance"""
    try:
        instance = db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id
        ).first()
        
        if not instance:
            raise HTTPException(status_code=404, detail="Workflow instance not found")
        
        return {
            "success": True,
            "data": {
                "instance": {
                    "id": instance.id,
                    "name": instance.name,
                    "template_id": instance.template_id,
                    "workflow_data": instance.workflow_data,
                    "status": instance.status,
                    "input_data": instance.input_data,
                    "output_data": instance.output_data,
                    "error_message": instance.error_message,
                    "created_at": instance.created_at.isoformat() if instance.created_at else None,
                    "started_at": instance.started_at.isoformat() if instance.started_at else None,
                    "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
                    "created_by": instance.created_by
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Enhanced Instance Execution Endpoints

@router.post("/instances/{instance_id}/execute")
async def execute_workflow_instance(
    instance_id: str,
    input_data: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = None,
    execution_engine: WorkflowExecutionEngine = Depends(get_execution_engine),
    db: Session = Depends(get_db)
):
    """Execute a workflow instance with real-time updates"""
    try:
        # Check if instance exists
        instance = db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id
        ).first()
        
        if not instance:
            raise HTTPException(status_code=404, detail="Workflow instance not found")
        
        # Check if already running
        current_status = execution_engine.get_execution_status(instance_id)
        if current_status.get("is_running"):
            raise HTTPException(status_code=400, detail="Workflow is already running")
        
        # Start execution in background
        if background_tasks:
            background_tasks.add_task(
                execution_engine.execute_workflow,
                instance_id,
                input_data or {}
            )
            
            return {
                "success": True,
                "message": "Workflow execution started",
                "instance_id": instance_id,
                "status": "starting"
            }
        else:
            # Execute synchronously (for testing)
            result = await execution_engine.execute_workflow(instance_id, input_data or {})
            
            return {
                "success": True,
                "message": "Workflow execution completed",
                "instance_id": instance_id,
                "status": "completed",
                "result": result
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/instances/{instance_id}/stop")
async def stop_workflow_execution(
    instance_id: str,
    execution_engine: WorkflowExecutionEngine = Depends(get_execution_engine)
):
    """Stop a running workflow execution"""
    try:
        success = await execution_engine.stop_execution(instance_id)
        
        if success:
            return {
                "success": True,
                "message": "Workflow execution stopped",
                "instance_id": instance_id
            }
        else:
            raise HTTPException(status_code=404, detail="No running execution found for this instance")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances/{instance_id}/status")
async def get_execution_status(
    instance_id: str,
    execution_engine: WorkflowExecutionEngine = Depends(get_execution_engine)
):
    """Get current execution status for a workflow instance"""
    try:
        status = execution_engine.get_execution_status(instance_id)
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances/{instance_id}/logs")
async def get_execution_logs(
    instance_id: str,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    db: Session = Depends(get_db)
):
    """Get execution logs for a workflow instance"""
    try:
        logs = db.query(WorkflowExecutionStep).filter(
            WorkflowExecutionStep.workflow_instance_id == instance_id
        ).order_by(WorkflowExecutionStep.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "steps": [
                    {
                        "id": log.id,
                        "step_name": log.step_name,
                        "step_type": log.step_type,
                        "node_id": log.node_id,
                        "status": log.status,
                        "created_at": log.created_at.isoformat() if log.created_at else None,
                        "started_at": log.started_at.isoformat() if log.started_at else None,
                        "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                        "execution_time_ms": log.execution_time_ms,
                        "error_message": log.error_message,
                        "input_data": log.input_data,
                        "output_data": log.output_data,
                        "logs": []  # For compatibility
                    }
                    for log in logs
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/instances/{instance_id}/execute-legacy")
async def execute_workflow_instance_legacy(
    instance_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Execute a workflow instance (legacy method - deprecated, use new execute endpoint)"""
    raise HTTPException(status_code=501, detail="Legacy execution method deprecated. Use /instances/{instance_id}/execute instead.")


async def _execute_workflow_background(
    instance_id: str,
    workflow_data: Dict[str, Any],
    input_data: Dict[str, Any],
    executor: WorkflowExecutor,
    db: Session
):
    """Execute workflow in background"""
    try:
        # Prepare input data for workflow execution
        execution_input = {
            "workflow_instance_id": instance_id,
            "nodes": workflow_data.get("nodes", []),
            "edges": workflow_data.get("edges", []),
            **input_data
        }
        
        # Execute workflow
        result = await executor.execute_automation_workflow(execution_input)
        
        # Update instance with result
        instance = db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id
        ).first()
        
        if instance:
            instance.status = "completed" if result.get("status") == "completed" else "failed"
            instance.output_data = result
            instance.completed_at = datetime.now()
            
            if result.get("error"):
                instance.error_message = result.get("error_message", "Unknown error")
            
            db.commit()
        
    except Exception as e:
        # Update instance with error
        instance = db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id
        ).first()
        
        if instance:
            instance.status = "failed"
            instance.error_message = str(e)
            instance.completed_at = datetime.now()
            db.commit()


@router.get("/instances")
async def list_workflow_instances(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List workflow instances"""
    try:
        query = db.query(WorkflowInstance)
        
        if status:
            query = query.filter(WorkflowInstance.status == status)
        
        instances = query.offset(offset).limit(limit).all()
        
        # Return empty array if no instances exist
        return {
            "success": True,
            "data": {
                "instances": [
                    {
                        "id": instance.id,
                        "name": instance.name,
                        "status": instance.status,
                        "created_at": instance.created_at.isoformat(),
                        "started_at": instance.started_at.isoformat() if instance.started_at else None,
                        "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
                        "template_id": instance.template_id
                    }
                    for instance in instances
                ]
            }
        }
        
    except Exception as e:
        # Return empty array on error for development
        return {
            "success": True,
            "instances": []
        }


@router.get("/instances/{instance_id}")
async def get_workflow_instance(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific workflow instance"""
    try:
        instance = db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id
        ).first()
        
        if not instance:
            raise HTTPException(status_code=404, detail="Workflow instance not found")
        
        return {
            "success": True,
            "instance": {
                "id": instance.id,
                "name": instance.name,
                "status": instance.status,
                "workflow_data": instance.workflow_data,
                "input_data": instance.input_data,
                "output_data": instance.output_data,
                "error_message": instance.error_message,
                "created_at": instance.created_at.isoformat(),
                "started_at": instance.started_at.isoformat() if instance.started_at else None,
                "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
                "template_id": instance.template_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/google-sheets/process")
async def process_google_sheets(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Process Google Sheets data with automation workflow (legacy - needs update)"""
    raise HTTPException(status_code=501, detail="Google Sheets processing endpoint needs to be updated to use new execution engine")
    try:
        google_sheets_id = request_data.get("google_sheets_id")
        if not google_sheets_id:
            raise HTTPException(status_code=400, detail="Google Sheets ID is required")
        
        # Create input data for workflow
        input_data = {
            "google_sheets_id": google_sheets_id,
            "notification_settings": request_data.get("notification_settings", {}),
            "output_settings": request_data.get("output_settings", {})
        }
        
        # Execute workflow in background
        background_tasks.add_task(
            _execute_sheets_workflow,
            input_data,
            executor
        )
        
        return {
            "success": True,
            "message": "Google Sheets processing started",
            "sheets_id": google_sheets_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_sheets_workflow(
    input_data: Dict[str, Any],
    executor: WorkflowExecutor
):
    """Execute Google Sheets workflow in background"""
    try:
        result = await executor.execute_automation_workflow(input_data)
        # Result handling would be done here
        print(f"Sheets workflow completed: {result}")
    except Exception as e:
        print(f"Sheets workflow failed: {str(e)}")


@router.post("/reports/daily")
async def generate_daily_report(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate daily analytics report (legacy - needs update)"""
    raise HTTPException(status_code=501, detail="Daily report generation endpoint needs to be updated to use new execution engine")
    try:
        report_date = request_data.get("report_date")  # Optional, defaults to today
        
        # Execute daily report workflow in background
        background_tasks.add_task(
            _execute_daily_report,
            report_date,
            executor
        )
        
        return {
            "success": True,
            "message": "Daily report generation started",
            "report_date": report_date or datetime.now().strftime('%Y-%m-%d')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_daily_report(
    report_date: Optional[str],
    executor: WorkflowExecutor
):
    """Execute daily report workflow in background"""
    try:
        result = await executor.execute_daily_report_workflow(report_date)
        print(f"Daily report completed: {result}")
    except Exception as e:
        print(f"Daily report failed: {str(e)}")


@router.get("/analytics/daily")
async def get_daily_analytics(
    date: str,
    db: Session = Depends(get_db)
):
    """Get daily analytics data"""
    try:
        # For now, return mock analytics data
        from datetime import datetime
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get basic stats from database
        instances_count = db.query(WorkflowInstance).filter(
            func.date(WorkflowInstance.created_at) == target_date
        ).count()
        
        completed_count = db.query(WorkflowInstance).filter(
            func.date(WorkflowInstance.created_at) == target_date,
            WorkflowInstance.status == 'completed'
        ).count()
        
        return {
            "success": True,
            "data": {
                "date": date,
                "instances_created": instances_count,
                "instances_completed": completed_count,
                "success_rate": (completed_count / instances_count * 100) if instances_count > 0 else 0,
                "total_processing_time": 0,  # Mock data
                "average_processing_time": 0  # Mock data
            }
        }
    except Exception as e:
        # Return empty data on error
        return {
            "success": True,
            "data": {
                "date": date,
                "instances_created": 0,
                "instances_completed": 0,
                "success_rate": 0,
                "total_processing_time": 0,
                "average_processing_time": 0
            }
        }


@router.get("/analytics/weekly")
async def get_weekly_analytics(
    end_date: str,
    db: Session = Depends(get_db)
):
    """Get weekly analytics summary"""
    try:
        # For now, return mock weekly analytics data
        from datetime import datetime, timedelta
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d').date()
        start_datetime = end_datetime - timedelta(days=7)
        
        # Get basic weekly stats from database
        instances_count = db.query(WorkflowInstance).filter(
            func.date(WorkflowInstance.created_at) >= start_datetime,
            func.date(WorkflowInstance.created_at) <= end_datetime
        ).count()
        
        completed_count = db.query(WorkflowInstance).filter(
            func.date(WorkflowInstance.created_at) >= start_datetime,
            func.date(WorkflowInstance.created_at) <= end_datetime,
            WorkflowInstance.status == 'completed'
        ).count()
        
        return {
            "success": True,
            "data": {
                "start_date": start_datetime.isoformat(),
                "end_date": end_date,
                "instances_created": instances_count,
                "instances_completed": completed_count,
                "success_rate": (completed_count / instances_count * 100) if instances_count > 0 else 0,
                "daily_breakdown": []  # Mock data
            }
        }
    except Exception as e:
        # Return empty data on error
        return {
            "success": True,
            "data": {
                "start_date": end_date,
                "end_date": end_date,
                "instances_created": 0,
                "instances_completed": 0,
                "success_rate": 0,
                "daily_breakdown": []
            }
        }


@router.get("/task-logs")
async def get_task_logs(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get task logs with filtering"""
    try:
        query = db.query(WorkflowTaskLog)
        
        if status:
            query = query.filter(WorkflowTaskLog.status == status)
        
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(WorkflowTaskLog.created_at >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(WorkflowTaskLog.created_at <= end_datetime)
        
        logs = query.offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "logs": [
                    {
                        "id": log.id,
                        "task_id": log.task_id,
                        "sheet_id": log.sheet_id,
                        "status": log.status,
                        "input_description": log.input_description,
                        "output_format": log.output_format,
                        "model_specification": log.model_specification,
                        "processing_time_ms": log.processing_time_ms,
                        "error_message": log.error_message,
                        "created_at": log.created_at.isoformat(),
                        "completed_at": log.completed_at.isoformat() if log.completed_at else None
                    }
                    for log in logs
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===============================
# Workflow Editor Endpoints
# ===============================

@router.post("/editor/save", response_model=Dict[str, Any])
async def save_workflow(
    request: SaveWorkflowRequest,
    db: Session = Depends(get_db)
):
    """Save a workflow from the visual editor"""
    try:
        # Create new workflow template
        template = WorkflowTemplate(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            category=request.category,
            template_data=request.workflow_data.dict(),  # Fixed: WorkflowTemplate uses template_data field
            is_public=request.is_public,
            created_by="system"  # Replace with actual user ID
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return {
            "success": True,
            "data": {
                "workflow_id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "workflow_data": template.template_data,  # Fixed: WorkflowTemplate has template_data field
                "is_public": template.is_public,
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "updated_at": template.updated_at.isoformat() if template.updated_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/editor/load/{workflow_id}", response_model=Dict[str, Any])
async def load_workflow(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """Load a workflow for the visual editor"""
    try:
        template = db.query(WorkflowTemplate).filter(WorkflowTemplate.id == workflow_id).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "success": True,
            "data": {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "workflow_data": template.template_data,  # Fixed: use template_data field
                "is_public": template.is_public,
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat() if template.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/editor/update/{workflow_id}", response_model=Dict[str, Any])
async def update_workflow(
    workflow_id: str,
    request: UpdateWorkflowRequest,
    db: Session = Depends(get_db)
):
    """Update a workflow from the visual editor"""
    try:
        template = db.query(WorkflowTemplate).filter(WorkflowTemplate.id == workflow_id).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Update fields if provided
        if request.name is not None:
            template.name = request.name
        if request.description is not None:
            template.description = request.description
        if request.category is not None:
            template.category = request.category
        if request.workflow_data is not None:
            template.workflow_data = request.workflow_data.dict()
        if request.is_public is not None:
            template.is_public = request.is_public
        
        template.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(template)
        
        return {
            "success": True,
            "data": {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "workflow_data": template.workflow_data,
                "is_public": template.is_public,
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/editor/delete/{workflow_id}", response_model=Dict[str, Any])
async def delete_workflow(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """Delete a workflow"""
    try:
        template = db.query(WorkflowTemplate).filter(WorkflowTemplate.id == workflow_id).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        db.delete(template)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "message": "Workflow deleted successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/editor/list", response_model=Dict[str, Any])
async def list_editor_workflows(
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List workflows for the editor"""
    try:
        query = db.query(WorkflowTemplate)
        
        if category:
            query = query.filter(WorkflowTemplate.category == category)
        
        if is_public is not None:
            query = query.filter(WorkflowTemplate.is_public == is_public)
        
        templates = query.order_by(WorkflowTemplate.updated_at.desc()).all()
        
        return {
            "success": True,
            "data": {
                "workflows": [
                    {
                        "id": template.id,
                        "name": template.name,
                        "description": template.description,
                        "category": template.category,
                        "is_public": template.is_public,
                        "created_at": template.created_at.isoformat() if template.created_at else None,
                        "updated_at": template.updated_at.isoformat() if template.updated_at else None
                    }
                    for template in templates
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===============================
# Email Report Endpoints
# ===============================

@router.post("/instances/{instance_id}/send-report")
async def send_workflow_execution_report(
    instance_id: str,
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send comprehensive workflow execution report via email
    
    Expected request_data:
    {
        "recipient_email": "user@example.com",
        "include_analytics": true,
        "include_detailed_logs": true
    }
    """
    try:
        # Validate inputs
        recipient_email = request_data.get("recipient_email")
        if not recipient_email:
            raise HTTPException(status_code=400, detail="recipient_email is required")
        
        include_analytics = request_data.get("include_analytics", True)
        include_detailed_logs = request_data.get("include_detailed_logs", True)
        
        # Get workflow instance
        instance = db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id
        ).first()
        
        if not instance:
            raise HTTPException(status_code=404, detail="Workflow instance not found")
        
        # Get execution logs and events
        execution_steps = db.query(WorkflowExecutionStep).filter(
            WorkflowExecutionStep.workflow_instance_id == instance_id
        ).order_by(WorkflowExecutionStep.created_at.asc()).all()
        
        # Convert to format expected by email service
        execution_logs = []
        execution_events = []
        
        for step in execution_steps:
            # Add as log entry
            log_level = 'error' if step.status == 'failed' else 'success' if step.status == 'completed' else 'info'
            execution_logs.append({
                'timestamp': step.created_at.isoformat() if step.created_at else datetime.now().isoformat(),
                'level': log_level,
                'message': f"Step {step.step_name}: {step.status}",
                'node_id': step.node_id,
                'execution_time': step.execution_time_ms,
                'details': {
                    'step_type': step.step_type,
                    'input_data': step.input_data,
                    'output_data': step.output_data,
                    'error_message': step.error_message
                }
            })
            
            # Add as event
            execution_events.append({
                'timestamp': step.started_at.isoformat() if step.started_at else step.created_at.isoformat(),
                'event_type': f"step_{step.status}",
                'data': {
                    'node_id': step.node_id,
                    'step_name': step.step_name,
                    'step_type': step.step_type,
                    'execution_time_ms': step.execution_time_ms
                }
            })
        
        # Create execution summary
        execution_data = {
            'start_time': instance.started_at.isoformat() if instance.started_at else instance.created_at.isoformat(),
            'end_time': instance.completed_at.isoformat() if instance.completed_at else None,
            'status': instance.status,
            'total_steps': len(execution_steps),
            'completed_steps': len([s for s in execution_steps if s.status == 'completed']),
            'failed_steps': len([s for s in execution_steps if s.status == 'failed'])
        }
        
        execution_summary = create_execution_summary_from_data(
            workflow_name=instance.name,
            instance_id=instance_id,
            execution_data=execution_data,
            logs=execution_logs,
            events=execution_events
        )
        
        # Initialize email service using settings
        try:
            from ...core.config import settings
            email_service = EmailService(
                smtp_server=settings.SMTP_SERVER,
                smtp_port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS
            )
            email_report_service = EmailReportService(email_service)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize email service: {str(e)}")
        
        # Send report in background
        background_tasks.add_task(
            _send_execution_report_background,
            email_report_service,
            recipient_email,
            execution_summary,
            execution_logs,
            execution_events,
            include_analytics,
            include_detailed_logs
        )
        
        return {
            "success": True,
            "message": "Workflow execution report is being sent",
            "recipient_email": recipient_email,
            "instance_id": instance_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/daily-analytics")
async def send_daily_analytics_report(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send daily analytics report via email
    
    Expected request_data:
    {
        "recipient_email": "user@example.com",
        "date": "2025-08-04"  # Optional, defaults to today
    }
    """
    try:
        # Validate inputs
        recipient_email = request_data.get("recipient_email")
        if not recipient_email:
            raise HTTPException(status_code=400, detail="recipient_email is required")
        
        report_date_str = request_data.get("date", datetime.now().strftime('%Y-%m-%d'))
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d')
        
        # Add timezone awareness to avoid offset-naive errors
        from datetime import timezone
        report_date = report_date.replace(tzinfo=timezone.utc)
        
        date_range = (
            report_date.replace(hour=0, minute=0, second=0, microsecond=0),
            report_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        
        # Get analytics data from database
        instances_query = db.query(WorkflowInstance).filter(
            WorkflowInstance.created_at >= date_range[0],
            WorkflowInstance.created_at <= date_range[1]
        )
        
        total_executions = instances_query.count()
        successful_executions = instances_query.filter(WorkflowInstance.status == 'completed').count()
        failed_executions = instances_query.filter(WorkflowInstance.status == 'failed').count()
        
        # Calculate average execution time
        completed_instances = instances_query.filter(
            WorkflowInstance.status == 'completed',
            WorkflowInstance.started_at.isnot(None),
            WorkflowInstance.completed_at.isnot(None)
        ).all()
        
        if completed_instances:
            execution_times = []
            for instance in completed_instances:
                if instance.started_at and instance.completed_at:
                    # Ensure both timestamps have timezone info
                    started_at = instance.started_at
                    completed_at = instance.completed_at
                    
                    # Add UTC timezone if none
                    if started_at.tzinfo is None:
                        started_at = started_at.replace(tzinfo=timezone.utc)
                    if completed_at.tzinfo is None:
                        completed_at = completed_at.replace(tzinfo=timezone.utc)
                    
                    duration = (completed_at - started_at).total_seconds()
                    execution_times.append(duration)
            average_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        else:
            average_execution_time = 0
        
        # Get error breakdown from execution steps
        error_steps = db.query(WorkflowExecutionStep).join(WorkflowInstance).filter(
            WorkflowInstance.created_at >= date_range[0],
            WorkflowInstance.created_at <= date_range[1],
            WorkflowExecutionStep.status == 'failed'
        ).all()
        
        error_breakdown = {}
        for step in error_steps:
            error_type = step.step_type or 'unknown'
            error_breakdown[error_type] = error_breakdown.get(error_type, 0) + 1
        
        # Create analytics object
        analytics = WorkflowAnalytics(
            total_executions=total_executions,
            successful_executions=successful_executions,
            failed_executions=failed_executions,
            average_execution_time=average_execution_time,
            success_rate_percentage=(successful_executions / total_executions * 100) if total_executions > 0 else 0,
            error_breakdown=error_breakdown,
            performance_trend=[]  # Could be enhanced with hourly data
        )
        
        # Get recent executions for the report
        recent_instances = instances_query.order_by(WorkflowInstance.created_at.desc()).limit(10).all()
        recent_executions = []
        
        for instance in recent_instances:
            execution_data = {
                'start_time': instance.started_at.isoformat() if instance.started_at else instance.created_at.isoformat(),
                'end_time': instance.completed_at.isoformat() if instance.completed_at else None,
                'status': instance.status,
                'total_steps': 0,  # Would need to count from execution steps
                'completed_steps': 0,
                'failed_steps': 0
            }
            
            # Get step counts for this instance
            steps = db.query(WorkflowExecutionStep).filter(
                WorkflowExecutionStep.workflow_instance_id == instance.id
            ).all()
            
            execution_data['total_steps'] = len(steps)
            execution_data['completed_steps'] = len([s for s in steps if s.status == 'completed'])
            execution_data['failed_steps'] = len([s for s in steps if s.status == 'failed'])
            
            execution_summary = create_execution_summary_from_data(
                workflow_name=instance.name,
                instance_id=instance.id,
                execution_data=execution_data,
                logs=[],
                events=[]
            )
            recent_executions.append(execution_summary)
        
        # Initialize email service using settings
        try:
            from ...core.config import settings
            email_service = EmailService(
                smtp_server=settings.SMTP_SERVER,
                smtp_port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS
            )
            email_report_service = EmailReportService(email_service)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize email service: {str(e)}")
        
        # Send report in background
        background_tasks.add_task(
            _send_daily_analytics_report_background,
            email_report_service,
            recipient_email,
            analytics,
            date_range,
            recent_executions
        )
        
        return {
            "success": True,
            "message": "Daily analytics report is being sent",
            "recipient_email": recipient_email,
            "report_date": report_date_str,
            "analytics_summary": {
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "success_rate": analytics.success_rate_percentage
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/execution")
async def send_execution_report(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send execution report via email
    
    Expected request_data:
    {
        "recipient_email": "user@example.com",
        "workflow_name": "Test Workflow",
        "subject_prefix": "Workflow Report"  # Optional
    }
    """
    try:
        # Validate inputs
        recipient_email = request_data.get("recipient_email")
        if not recipient_email:
            raise HTTPException(status_code=400, detail="recipient_email is required")
        
        workflow_name = request_data.get("workflow_name", "Test Workflow")
        subject_prefix = request_data.get("subject_prefix", "Workflow Report")
        
        # Create a sample execution summary for testing
        from ...services.workflow.email_report_service import create_execution_summary_from_data
        
        execution_data = {
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat(),
            'status': 'completed',
            'total_steps': 3,
            'completed_steps': 3,
            'failed_steps': 0
        }
        
        execution_summary = create_execution_summary_from_data(
            workflow_name=workflow_name,
            instance_id="test-instance-" + str(datetime.now().timestamp()),
            execution_data=execution_data,
            logs=[
                {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'INFO',
                    'message': 'Workflow started successfully'
                },
                {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'INFO',
                    'message': 'All steps completed successfully'
                }
            ],
            events=[
                {
                    'timestamp': datetime.now().isoformat(),
                    'event_type': 'workflow_started',
                    'data': {'workflow_name': workflow_name}
                },
                {
                    'timestamp': datetime.now().isoformat(),
                    'event_type': 'workflow_completed',
                    'data': {'duration': '30s', 'status': 'success'}
                }
            ]
        )
        
        # Initialize email service
        try:
            from ...services.workflow.email_report_service import EmailReportService
            from ...services.workflow.notifications import EmailService
            from ...core.config import settings
            
            # Create EmailService first
            email_service = EmailService(
                smtp_server=settings.SMTP_SERVER,
                smtp_port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS
            )
            
            # Create EmailReportService with EmailService
            email_report_service = EmailReportService(email_service)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize email service: {str(e)}")
        
        # Send report in background
        background_tasks.add_task(
            _send_execution_report_background,
            email_report_service,
            recipient_email,
            execution_summary,
            [],  # logs
            [],  # events
            True,  # include_analytics
            True   # include_detailed_logs
        )
        
        return {
            "success": True,
            "message": "Execution report is being sent",
            "recipient_email": recipient_email,
            "workflow_name": workflow_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _send_execution_report_background(
    email_report_service: EmailReportService,
    recipient_email: str,
    execution_summary: WorkflowExecutionSummary,
    execution_logs: List[Dict[str, Any]],
    execution_events: List[Dict[str, Any]],
    include_analytics: bool,
    include_detailed_logs: bool
):
    """Send execution report in background"""
    try:
        result = await email_report_service.send_workflow_completion_report(
            recipient_email=recipient_email,
            execution_summary=execution_summary,
            execution_logs=execution_logs,
            execution_events=execution_events,
            include_analytics=include_analytics,
            include_detailed_logs=include_detailed_logs
        )
        print(f"Execution report sent: {result}")
    except Exception as e:
        print(f"Failed to send execution report: {str(e)}")


async def _send_daily_analytics_report_background(
    email_report_service: EmailReportService,
    recipient_email: str,
    analytics: WorkflowAnalytics,
    date_range: tuple,
    recent_executions: List[WorkflowExecutionSummary]
):
    """Send daily analytics report in background"""
    try:
        result = await email_report_service.send_daily_analytics_report(
            recipient_email=recipient_email,
            analytics=analytics,
            date_range=date_range,
            recent_executions=recent_executions
        )
        print(f"Daily analytics report sent: {result}")
    except Exception as e:
        print(f"Failed to send daily analytics report: {str(e)}")


# Add missing import for os
import os
