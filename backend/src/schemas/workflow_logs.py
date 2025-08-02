"""
Pydantic schemas for workflow logging API responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class WorkflowTaskLogResponse(BaseModel):
    """Response schema for workflow task logs"""
    
    id: str
    task_id: str
    task_name: str
    task_type: Optional[str] = None
    status: Optional[str] = None
    log_level: Optional[str] = None
    
    # Input/Output tracking
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    expected_output: Optional[Dict[str, Any]] = None
    
    # Success/Failure details
    success_criteria: Optional[Dict[str, Any]] = None
    failure_reason: Optional[str] = None
    error_code: Optional[str] = None
    error_stack_trace: Optional[str] = None
    
    # Performance metrics
    processing_time_ms: Optional[int] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    # External integrations
    sheet_id: Optional[str] = None
    row_number: Optional[int] = None
    api_endpoint: Optional[str] = None
    api_response_code: Optional[int] = None
    
    # Metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WorkflowExecutionStepResponse(BaseModel):
    """Response schema for workflow execution steps"""
    
    id: str
    workflow_instance_id: str
    step_name: Optional[str] = None
    step_type: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    log_level: Optional[str] = None
    component_version: Optional[str] = None
    user_id: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    artifacts: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LogQueryParams(BaseModel):
    """Query parameters for log filtering"""
    
    workflow_instance_id: Optional[str] = None
    task_type: Optional[str] = None
    status: Optional[str] = None
    log_level: Optional[str] = None
    user_id: Optional[str] = None
    limit: int = Field(50, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class LogSummaryResponse(BaseModel):
    """Summary statistics for workflow logs"""
    
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    processing_tasks: int
    success_rate: float = Field(description="Success rate as percentage")
    average_execution_time_ms: float
    time_range_hours: int
    error_distribution: Dict[str, int] = Field(description="Count of each error type")
    task_type_distribution: Dict[str, int] = Field(description="Count of each task type")


class TaskPerformanceMetrics(BaseModel):
    """Performance metrics for individual tasks"""
    
    task_id: str
    task_name: str
    task_type: str
    execution_time_ms: int
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    success: bool
    timestamp: datetime


class WorkflowAnalytics(BaseModel):
    """Analytics data for workflow performance"""
    
    instance_id: str
    total_execution_time_ms: int
    step_count: int
    success_rate: float
    bottleneck_steps: List[str] = Field(description="Steps that took longest to execute")
    error_prone_steps: List[str] = Field(description="Steps that fail most often")
    performance_trend: Dict[str, float] = Field(description="Performance over time")


class LogExportRequest(BaseModel):
    """Request schema for exporting logs"""
    
    format: str = Field("json", description="Export format: json, csv, xlsx")
    filters: LogQueryParams
    include_stack_traces: bool = False
    include_performance_metrics: bool = True


class NotificationSettings(BaseModel):
    """Settings for log-based notifications"""
    
    email_on_failure: bool = False
    slack_webhook_url: Optional[str] = None
    failure_threshold: int = Field(3, description="Number of failures before notification")
    notification_cooldown_minutes: int = Field(30, description="Cooldown between notifications")
