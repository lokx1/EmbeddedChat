"""
Workflow State Management using Pydantic Models
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class WorkflowState(BaseModel):
    """Main workflow state that persists across all steps"""
    
    # Workflow metadata
    workflow_instance_id: str
    status: str = "running"  # running, completed, failed, paused
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Workflow configuration
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Execution tracking
    current_step: Optional[str] = None
    completed_steps: List[str] = Field(default_factory=list)
    failed_steps: List[str] = Field(default_factory=list)
    step_outputs: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Input/Output data
    initial_input: Dict[str, Any] = Field(default_factory=dict)
    final_output: Dict[str, Any] = Field(default_factory=dict)
    
    # Google Sheets specific data
    google_sheets_data: Dict[str, Any] = Field(default_factory=dict)
    processed_rows: List[int] = Field(default_factory=list)
    
    # Generated content tracking
    generated_files: List[Dict[str, Any]] = Field(default_factory=list)
    google_drive_files: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Notification tracking
    notifications_sent: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Error tracking
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    retry_counts: Dict[str, int] = Field(default_factory=dict)
    
    # Performance metrics
    execution_start_time: Optional[datetime] = None
    execution_end_time: Optional[datetime] = None
    step_execution_times: Dict[str, int] = Field(default_factory=dict)  # in milliseconds
    
    def add_error(self, node_id: str, error_message: str, error_type: str = "unknown"):
        """Add an error to the workflow state"""
        self.errors.append({
            "node_id": node_id,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        })
        if node_id not in self.failed_steps:
            self.failed_steps.append(node_id)
    
    def mark_step_complete(self, node_id: str, output_data: Dict[str, Any], execution_time_ms: int):
        """Mark a step as completed with its output data"""
        if node_id not in self.completed_steps:
            self.completed_steps.append(node_id)
        self.step_outputs[node_id] = output_data
        self.step_execution_times[node_id] = execution_time_ms
        self.updated_at = datetime.now()
    
    def get_step_output(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get the output data from a specific step"""
        return self.step_outputs.get(node_id)
    
    def is_step_completed(self, node_id: str) -> bool:
        """Check if a step has been completed"""
        return node_id in self.completed_steps
    
    def is_step_failed(self, node_id: str) -> bool:
        """Check if a step has failed"""
        return node_id in self.failed_steps
    
    def get_retry_count(self, node_id: str) -> int:
        """Get the retry count for a specific step"""
        return self.retry_counts.get(node_id, 0)
    
    def increment_retry_count(self, node_id: str):
        """Increment the retry count for a specific step"""
        self.retry_counts[node_id] = self.retry_counts.get(node_id, 0) + 1
    
    def add_generated_file(self, file_info: Dict[str, Any]):
        """Add information about a generated file"""
        self.generated_files.append({
            **file_info,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_google_drive_file(self, file_info: Dict[str, Any]):
        """Add information about a file stored in Google Drive"""
        self.google_drive_files.append({
            **file_info,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_notification(self, notification_info: Dict[str, Any]):
        """Add information about a sent notification"""
        self.notifications_sent.append({
            **notification_info,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the workflow execution"""
        total_steps = len(self.nodes)
        completed_count = len(self.completed_steps)
        failed_count = len(self.failed_steps)
        
        execution_time = None
        if self.execution_start_time and self.execution_end_time:
            execution_time = (self.execution_end_time - self.execution_start_time).total_seconds()
        
        return {
            "workflow_instance_id": self.workflow_instance_id,
            "status": self.status,
            "total_steps": total_steps,
            "completed_steps": completed_count,
            "failed_steps": failed_count,
            "success_rate": (completed_count / total_steps * 100) if total_steps > 0 else 0,
            "execution_time_seconds": execution_time,
            "generated_files_count": len(self.generated_files),
            "notifications_sent_count": len(self.notifications_sent),
            "errors_count": len(self.errors),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class TaskLogState(BaseModel):
    """State for individual task logging from Google Sheets"""
    
    task_id: str
    sheet_id: str
    row_number: int
    input_description: str
    input_asset_urls: List[str] = Field(default_factory=list)
    output_format: str
    model_specification: str
    status: str = "pending"  # pending, processing, success, failed
    output_file_urls: List[str] = Field(default_factory=list)
    google_drive_folder_id: Optional[str] = None
    error_message: Optional[str] = None
    processing_start_time: Optional[datetime] = None
    processing_end_time: Optional[datetime] = None
    email_notification_sent: bool = False
    slack_notification_sent: bool = False
    
    def get_processing_time_ms(self) -> Optional[int]:
        """Get processing time in milliseconds"""
        if self.processing_start_time and self.processing_end_time:
            return int((self.processing_end_time - self.processing_start_time).total_seconds() * 1000)
        return None
    
    def mark_success(self, output_urls: List[str]):
        """Mark the task as successful"""
        self.status = "success"
        self.output_file_urls = output_urls
        self.processing_end_time = datetime.now()
    
    def mark_failed(self, error_message: str):
        """Mark the task as failed"""
        self.status = "failed"
        self.error_message = error_message
        self.processing_end_time = datetime.now()


class DailyReportState(BaseModel):
    """State for daily report generation"""
    
    report_date: str  # YYYY-MM-DD format
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    success_rate: float = 0.0
    error_breakdown: Dict[str, int] = Field(default_factory=dict)
    analytics_chart_generated: bool = False
    analytics_chart_url: Optional[str] = None
    report_sent: bool = False
    generated_at: datetime = Field(default_factory=datetime.now)
    
    def calculate_success_rate(self):
        """Calculate and update the success rate"""
        if self.total_tasks > 0:
            self.success_rate = (self.successful_tasks / self.total_tasks) * 100
        else:
            self.success_rate = 0.0
    
    def add_error_to_breakdown(self, error_type: str):
        """Add an error to the breakdown"""
        self.error_breakdown[error_type] = self.error_breakdown.get(error_type, 0) + 1
