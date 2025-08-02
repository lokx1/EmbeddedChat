"""
Main Workflow Engine using LlamaIndex Workflow Framework
"""
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Context
)

from .events import (
    WorkflowStartEvent,
    GoogleSheetsEvent,
    AIGenerationEvent,
    FileStorageEvent,
    NotificationEvent,
    LoggingEvent,
    ReportGenerationEvent,
    WorkflowCompleteEvent,
    WorkflowErrorEvent,
    StepCompleteEvent
)
from .state import WorkflowState, TaskLogState
from .ai_providers import AIProviderFactory
from .google_services import GoogleServicesManager
from .notifications import NotificationManager
from .analytics import AnalyticsService


class AutomationWorkflow(Workflow):
    """Main automation workflow for Google Sheets processing"""
    
    def __init__(
        self,
        google_services: GoogleServicesManager,
        notification_manager: NotificationManager,
        analytics_service: AnalyticsService,
        ai_config: Dict[str, Dict[str, Any]],
        timeout: int = 3600,  # 1 hour timeout
        verbose: bool = True
    ):
        super().__init__(timeout=timeout, verbose=verbose)
        self.google_services = google_services
        self.notification_manager = notification_manager
        self.analytics_service = analytics_service
        self.ai_config = ai_config
        
        # Initialize AI providers
        self.ai_providers = {}
        for provider_name, config in ai_config.items():
            try:
                provider = AIProviderFactory.create_provider(provider_name, **config)
                self.ai_providers[provider_name] = provider
            except Exception as e:
                print(f"Warning: Could not initialize {provider_name} provider: {str(e)}")
    
    @step
    async def start_workflow(
        self, 
        ctx: Context[WorkflowState], 
        ev: StartEvent
    ) -> GoogleSheetsEvent | WorkflowErrorEvent:
        """Initialize and start the workflow"""
        try:
            # Initialize workflow state
            workflow_state = WorkflowState(
                workflow_instance_id=ev.workflow_instance_id,
                nodes=ev.input_data.get('nodes', []),
                edges=ev.input_data.get('edges', []),
                initial_input=ev.input_data,
                execution_start_time=datetime.now()
            )
            
            # Store state in context
            async with ctx.store.edit_state() as state:
                for key, value in workflow_state.model_dump().items():
                    state[key] = value
            
            # Extract Google Sheets ID from input
            sheet_id = ev.input_data.get('google_sheets_id')
            if not sheet_id:
                return WorkflowErrorEvent(
                    workflow_instance_id=ev.workflow_instance_id,
                    node_id="start",
                    error_type="configuration_error",
                    error_message="Google Sheets ID not provided"
                )
            
            return GoogleSheetsEvent(sheet_id=sheet_id)
            
        except Exception as e:
            return WorkflowErrorEvent(
                workflow_instance_id="unknown",
                node_id="start",
                error_type="initialization_error",
                error_message=str(e)
            )
    
    @step
    async def process_google_sheets(
        self, 
        ctx: Context[WorkflowState], 
        ev: GoogleSheetsEvent
    ) -> AIGenerationEvent | WorkflowErrorEvent:
        """Process Google Sheets data and extract tasks"""
        try:
            # Process sheet data
            sheet_tasks = await self.google_services.process_sheet_for_workflow(ev.sheet_id)
            
            # Update state with sheet data
            async with ctx.store.edit_state() as state:
                state["google_sheets_data"] = {
                    "sheet_id": ev.sheet_id,
                    "tasks": sheet_tasks,
                    "processed_at": datetime.now().isoformat()
                }
            
            if not sheet_tasks:
                return WorkflowErrorEvent(
                    workflow_instance_id=state.get("workflow_instance_id", "unknown"),
                    node_id="google_sheets",
                    error_type="no_data_error",
                    error_message="No valid tasks found in Google Sheets"
                )
            
            # Create workflow output folder
            workflow_folder_id = await self.google_services.create_workflow_output_folder(
                state.get("workflow_instance_id")
            )
            
            async with ctx.store.edit_state() as state:
                state["google_drive_folder_id"] = workflow_folder_id
            
            # Send multiple AI generation events for parallel processing
            for task in sheet_tasks:
                ctx.send_event(AIGenerationEvent(
                    node_id=f"ai_generation_{task['task_id']}",
                    provider=task['model_specification'].lower(),
                    model_name=self._get_model_name(task['model_specification']),
                    prompt=task['input_description'],
                    input_description=task['input_description'],
                    asset_urls=task['input_asset_urls'],
                    output_format=task['output_format']
                ))
            
            return None  # No direct return, events sent via ctx.send_event
            
        except Exception as e:
            workflow_instance_id = await ctx.store.get("workflow_instance_id", "unknown")
            return WorkflowErrorEvent(
                workflow_instance_id=workflow_instance_id,
                node_id="google_sheets",
                error_type="sheets_processing_error",
                error_message=str(e)
            )
    
    @step(num_workers=4)  # Allow parallel AI processing
    async def generate_ai_content(
        self, 
        ctx: Context[WorkflowState], 
        ev: AIGenerationEvent
    ) -> FileStorageEvent | WorkflowErrorEvent:
        """Generate content using AI providers"""
        try:
            # Get AI provider
            provider = self.ai_providers.get(ev.provider.lower())
            if not provider:
                return WorkflowErrorEvent(
                    workflow_instance_id=await ctx.store.get("workflow_instance_id", "unknown"),
                    node_id=ev.node_id,
                    error_type="provider_error",
                    error_message=f"AI provider '{ev.provider}' not available"
                )
            
            start_time = datetime.now()
            
            # Generate content - handle both sync and async providers
            if hasattr(provider, '__class__') and 'Ollama' in provider.__class__.__name__:
                # Ollama provider is sync
                if ev.asset_urls:
                    result = provider.process_with_assets(
                        ev.input_description,
                        ev.asset_urls,
                        ev.output_format,
                        ev.model_name
                    )
                else:
                    result = provider.generate_content(
                        ev.prompt,
                        ev.output_format,
                        ev.model_name
                    )
            else:
                # Other providers are async
                if ev.asset_urls:
                    result = await provider.process_with_assets(
                        ev.input_description,
                        ev.asset_urls,
                        ev.output_format,
                        ev.model_name
                    )
                else:
                    result = await provider.generate_content(
                        ev.prompt,
                        ev.output_format,
                        ev.model_name
                    )
            
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            if not result.get('success'):
                return WorkflowErrorEvent(
                    workflow_instance_id=await ctx.store.get("workflow_instance_id", "unknown"),
                    node_id=ev.node_id,
                    error_type="ai_generation_error",
                    error_message=result.get('error', 'Unknown AI generation error')
                )
            
            # Update state with generation result
            async with ctx.store.edit_state() as state:
                if "generation_results" not in state:
                    state["generation_results"] = {}
                state["generation_results"][ev.node_id] = {
                    "result": result,
                    "execution_time_ms": execution_time_ms,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare file for storage
            file_name = f"{ev.node_id}_{int(datetime.now().timestamp())}.{ev.output_format.lower()}"
            
            return FileStorageEvent(
                node_id=ev.node_id,
                file_data=result['content'] if isinstance(result['content'], bytes) else result['content'].encode(),
                file_name=file_name,
                file_type=result.get('content_type', 'application/octet-stream'),
                google_drive_folder_id=await ctx.store.get("google_drive_folder_id")
            )
            
        except Exception as e:
            return WorkflowErrorEvent(
                workflow_instance_id=await ctx.store.get("workflow_instance_id", "unknown"),
                node_id=ev.node_id,
                error_type="ai_generation_exception",
                error_message=str(e)
            )
    
    @step(num_workers=4)  # Allow parallel file storage
    async def store_generated_file(
        self, 
        ctx: Context[WorkflowState], 
        ev: FileStorageEvent
    ) -> LoggingEvent | WorkflowErrorEvent:
        """Store generated files in Google Drive"""
        try:
            # Upload file to Google Drive
            upload_result = await self.google_services.store_workflow_file(
                ev.file_data,
                ev.file_name,
                ev.file_type,
                ev.google_drive_folder_id
            )
            
            # Update state with file information
            async with ctx.store.edit_state() as state:
                if "stored_files" not in state:
                    state["stored_files"] = {}
                state["stored_files"][ev.node_id] = {
                    "upload_result": upload_result,
                    "file_name": ev.file_name,
                    "file_type": ev.file_type,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Extract task information for logging
            task_id = ev.node_id.replace("ai_generation_", "")
            
            return LoggingEvent(
                node_id=ev.node_id,
                task_id=task_id,
                status="success",
                details={
                    "file_info": upload_result,
                    "file_name": ev.file_name,
                    "file_type": ev.file_type
                },
                execution_time_ms=0  # Will be calculated in logging step
            )
            
        except Exception as e:
            return WorkflowErrorEvent(
                workflow_instance_id=await ctx.store.get("workflow_instance_id", "unknown"),
                node_id=ev.node_id,
                error_type="file_storage_error",
                error_message=str(e)
            )
    
    @step(num_workers=2)  # Allow parallel logging
    async def log_task_completion(
        self, 
        ctx: Context[WorkflowState], 
        ev: LoggingEvent
    ) -> NotificationEvent | WorkflowCompleteEvent:
        """Log task completion and trigger notifications"""
        try:
            # Get task details from state
            sheet_data = await ctx.store.get("google_sheets_data", {})
            generation_results = await ctx.store.get("generation_results", {})
            stored_files = await ctx.store.get("stored_files", {})
            
            # Find the specific task
            task_info = None
            for task in sheet_data.get("tasks", []):
                if task['task_id'] == ev.task_id:
                    task_info = task
                    break
            
            if not task_info:
                return WorkflowErrorEvent(
                    workflow_instance_id=await ctx.store.get("workflow_instance_id", "unknown"),
                    node_id=ev.node_id,
                    error_type="logging_error",
                    error_message="Task information not found"
                )
            
            # Calculate total execution time
            generation_time = generation_results.get(ev.node_id, {}).get("execution_time_ms", 0)
            
            # Create task log state
            task_log = TaskLogState(
                task_id=ev.task_id,
                sheet_id=task_info['sheet_id'],
                row_number=task_info['row_number'],
                input_description=task_info['input_description'],
                input_asset_urls=task_info['input_asset_urls'],
                output_format=task_info['output_format'],
                model_specification=task_info['model_specification'],
                status=ev.status,
                processing_start_time=datetime.now() - datetime.timedelta(milliseconds=generation_time),
                processing_end_time=datetime.now()
            )
            
            if ev.status == "success":
                file_info = stored_files.get(ev.node_id, {})
                output_urls = [file_info.get("upload_result", {}).get("web_view_link", "")]
                task_log.mark_success(output_urls)
            else:
                task_log.mark_failed(ev.error_message or "Unknown error")
            
            # Update workflow state
            async with ctx.store.edit_state() as state:
                if "completed_tasks" not in state:
                    state["completed_tasks"] = {}
                state["completed_tasks"][ev.task_id] = task_log.model_dump()
            
            # Send notification event
            return NotificationEvent(
                node_id=ev.node_id,
                notification_type="task_completion",
                recipient="admin",  # Will be configured based on settings
                subject=f"Task {ev.status}: {task_info['input_description'][:50]}...",
                message=f"Task {ev.task_id} completed with status: {ev.status}",
                success=ev.status == "success"
            )
            
        except Exception as e:
            return WorkflowErrorEvent(
                workflow_instance_id=await ctx.store.get("workflow_instance_id", "unknown"),
                node_id=ev.node_id,
                error_type="logging_exception",
                error_message=str(e)
            )
    
    @step
    async def send_notifications(
        self, 
        ctx: Context[WorkflowState], 
        ev: NotificationEvent
    ) -> StepCompleteEvent | WorkflowErrorEvent:
        """Send notifications for task completion"""
        try:
            # For now, just log the notification
            # In a real implementation, you would send actual emails/Slack messages
            
            async with ctx.store.edit_state() as state:
                if "notifications" not in state:
                    state["notifications"] = []
                state["notifications"].append({
                    "node_id": ev.node_id,
                    "type": ev.notification_type,
                    "subject": ev.subject,
                    "message": ev.message,
                    "success": ev.success,
                    "timestamp": datetime.now().isoformat()
                })
            
            return StepCompleteEvent(
                node_id=ev.node_id,
                step_name="notification",
                output_data={"notification_sent": True},
                success=True,
                execution_time_ms=100  # Minimal time for notification
            )
            
        except Exception as e:
            return WorkflowErrorEvent(
                workflow_instance_id=await ctx.store.get("workflow_instance_id", "unknown"),
                node_id=ev.node_id,
                error_type="notification_error",
                error_message=str(e)
            )
    
    @step
    async def complete_workflow(
        self, 
        ctx: Context[WorkflowState], 
        ev: StepCompleteEvent
    ) -> StopEvent | None:
        """Check if workflow is complete and finalize"""
        try:
            # Get current state
            completed_tasks = await ctx.store.get("completed_tasks", {})
            sheet_data = await ctx.store.get("google_sheets_data", {})
            total_tasks = len(sheet_data.get("tasks", []))
            
            # Check if all tasks are completed
            if len(completed_tasks) >= total_tasks:
                # Update workflow state
                async with ctx.store.edit_state() as state:
                    state["status"] = "completed"
                    state["execution_end_time"] = datetime.now().isoformat()
                
                # Generate final summary
                successful_tasks = len([task for task in completed_tasks.values() if task.get("status") == "success"])
                failed_tasks = len([task for task in completed_tasks.values() if task.get("status") == "failed"])
                
                final_output = {
                    "workflow_instance_id": await ctx.store.get("workflow_instance_id"),
                    "status": "completed",
                    "total_tasks": total_tasks,
                    "successful_tasks": successful_tasks,
                    "failed_tasks": failed_tasks,
                    "success_rate": (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                    "completed_tasks": completed_tasks,
                    "google_drive_folder_id": await ctx.store.get("google_drive_folder_id")
                }
                
                return StopEvent(result=final_output)
            
            # Not complete yet, wait for more tasks
            return None
            
        except Exception as e:
            return StopEvent(result={
                "error": "Workflow completion check failed",
                "error_message": str(e)
            })
    
    @step
    async def handle_workflow_error(
        self, 
        ctx: Context[WorkflowState], 
        ev: WorkflowErrorEvent
    ) -> StopEvent:
        """Handle workflow errors and cleanup"""
        try:
            # Update state with error
            async with ctx.store.edit_state() as state:
                state["status"] = "failed"
                state["execution_end_time"] = datetime.now().isoformat()
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "node_id": ev.node_id,
                    "error_type": ev.error_type,
                    "error_message": ev.error_message,
                    "retry_count": ev.retry_count,
                    "timestamp": datetime.now().isoformat()
                })
            
            return StopEvent(result={
                "workflow_instance_id": ev.workflow_instance_id,
                "status": "failed",
                "error_type": ev.error_type,
                "error_message": ev.error_message,
                "node_id": ev.node_id
            })
            
        except Exception as e:
            return StopEvent(result={
                "error": "Error handling failed",
                "error_message": str(e)
            })
    
    def _get_model_name(self, provider: str) -> str:
        """Get appropriate model name for provider"""
        provider_lower = provider.lower()
        if provider_lower == "openai":
            return "gpt-4o"
        elif provider_lower == "claude":
            return "claude-3-5-sonnet-20241022"
        elif provider_lower == "ollama":
            return "llama3.2"
        else:
            return "gpt-4o"  # Default fallback


class DailyReportWorkflow(Workflow):
    """Workflow for generating daily reports"""
    
    def __init__(
        self,
        analytics_service: AnalyticsService,
        notification_manager: NotificationManager,
        timeout: int = 600,
        verbose: bool = True
    ):
        super().__init__(timeout=timeout, verbose=verbose)
        self.analytics_service = analytics_service
        self.notification_manager = notification_manager
    
    @step
    async def generate_daily_report(
        self, 
        ctx: Context, 
        ev: StartEvent
    ) -> NotificationEvent | WorkflowErrorEvent:
        """Generate daily analytics report"""
        try:
            report_date = ev.report_date or datetime.now().strftime('%Y-%m-%d')
            
            # Generate report
            report_data = await self.analytics_service.generate_daily_report(report_date)
            
            # Store report data in context
            await ctx.store.set("report_data", report_data)
            
            return NotificationEvent(
                node_id="daily_report",
                notification_type="daily_report",
                recipient="admin",
                subject=f"Daily Workflow Report - {report_date}",
                message="Daily analytics report has been generated",
                success=True
            )
            
        except Exception as e:
            return WorkflowErrorEvent(
                workflow_instance_id="daily_report",
                node_id="report_generation",
                error_type="report_generation_error",
                error_message=str(e)
            )
    
    @step
    async def send_report_notification(
        self, 
        ctx: Context, 
        ev: NotificationEvent
    ) -> StopEvent:
        """Send daily report notifications"""
        try:
            report_data = await ctx.store.get("report_data")
            
            # Send notifications (implement based on your notification settings)
            # This would send actual emails/Slack messages in a real implementation
            
            return StopEvent(result={
                "status": "completed",
                "report_data": report_data,
                "notifications_sent": True
            })
            
        except Exception as e:
            return StopEvent(result={
                "status": "failed",
                "error": str(e)
            })


class WorkflowExecutor:
    """Main executor for workflow operations"""
    
    def __init__(
        self,
        google_services: GoogleServicesManager,
        notification_manager: NotificationManager,
        analytics_service: AnalyticsService,
        ai_config: Dict[str, Dict[str, Any]]
    ):
        self.google_services = google_services
        self.notification_manager = notification_manager
        self.analytics_service = analytics_service
        self.ai_config = ai_config
    
    async def execute_automation_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the main automation workflow"""
        
        workflow_instance_id = str(uuid.uuid4())
        
        # Create workflow
        workflow = AutomationWorkflow(
            google_services=self.google_services,
            notification_manager=self.notification_manager,
            analytics_service=self.analytics_service,
            ai_config=self.ai_config
        )
        
        # Run workflow
        result = await workflow.run(
            workflow_instance_id=workflow_instance_id,
            input_data=input_data
        )
        
        return result
    
    async def execute_daily_report_workflow(self, report_date: str = None) -> Dict[str, Any]:
        """Execute daily report generation workflow"""
        
        workflow = DailyReportWorkflow(
            analytics_service=self.analytics_service,
            notification_manager=self.notification_manager
        )
        
        result = await workflow.run(report_date=report_date)
        return result
