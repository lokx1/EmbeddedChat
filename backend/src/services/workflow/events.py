"""
Workflow Events for LlamaIndex Workflow Framework
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from llama_index.core.workflow import Event


class WorkflowStartEvent(Event):
    """Event to start the workflow execution"""
    workflow_instance_id: str
    input_data: Dict[str, Any]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class GoogleSheetsEvent(Event):
    """Event for processing Google Sheets data"""
    sheet_id: str
    sheet_range: Optional[str] = "A:Z"
    row_data: Optional[Dict[str, Any]] = None


class AIGenerationEvent(Event):
    """Event for AI content generation"""
    node_id: str
    provider: str  # ollama, openai, claude
    model_name: str
    prompt: str
    input_description: str
    asset_urls: List[str]
    output_format: str  # PNG, JPG, GIF, MP3
    generation_config: Dict[str, Any] = Field(default_factory=dict)


class FileStorageEvent(Event):
    """Event for storing generated files"""
    node_id: str
    file_data: bytes
    file_name: str
    file_type: str
    google_drive_folder_id: Optional[str] = None


class NotificationEvent(Event):
    """Event for sending notifications"""
    node_id: str
    notification_type: str  # email, slack
    recipient: str
    subject: str
    message: str
    success: bool
    attachments: Optional[List[str]] = None


class LoggingEvent(Event):
    """Event for logging task details"""
    node_id: str
    task_id: str
    status: str  # success, failure
    details: Dict[str, Any]
    execution_time_ms: int
    error_message: Optional[str] = None


class ReportGenerationEvent(Event):
    """Event for generating daily reports"""
    report_date: str  # YYYY-MM-DD format
    force_regenerate: bool = False


class WorkflowCompleteEvent(Event):
    """Event when workflow execution is complete"""
    workflow_instance_id: str
    status: str  # completed, failed
    output_data: Dict[str, Any]
    execution_summary: Dict[str, Any]


class WorkflowErrorEvent(Event):
    """Event for workflow errors"""
    workflow_instance_id: str
    node_id: str
    error_type: str
    error_message: str
    retry_count: int = 0


class TransformEvent(Event):
    """Event for data transformation steps"""
    node_id: str
    input_data: Dict[str, Any]
    transformation_type: str
    transformation_config: Dict[str, Any] = Field(default_factory=dict)


class ValidationEvent(Event):
    """Event for data validation"""
    node_id: str
    data_to_validate: Dict[str, Any]
    validation_rules: Dict[str, Any]


class StepCompleteEvent(Event):
    """Generic event for step completion"""
    node_id: str
    step_name: str
    output_data: Dict[str, Any]
    success: bool
    execution_time_ms: int
    next_nodes: List[str] = Field(default_factory=list)
