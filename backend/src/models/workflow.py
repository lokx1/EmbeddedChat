from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class WorkflowTemplate(Base):
    """Template for reusable workflows"""
    __tablename__ = "workflow_templates"
    
    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    template_data = Column(JSON, nullable=False)  # Node and edge configuration
    category = Column(String(100))
    is_public = Column(Boolean, default=False)
    created_by = Column(String, nullable=True)  # User ID who created this template
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow_instances = relationship("WorkflowInstance", back_populates="template")


class WorkflowInstance(Base):
    """Individual workflow execution instance"""
    __tablename__ = "workflow_instances"
    
    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    template_id = Column(String, ForeignKey("workflow_templates.id"), nullable=True)
    workflow_data = Column(JSON, nullable=False)  # Current node and edge configuration
    status = Column(String(50), default="draft")  # draft, running, completed, failed, paused
    input_data = Column(JSON)  # Input parameters for the workflow
    output_data = Column(JSON)  # Final results
    error_message = Column(Text)
    execution_logs = Column(JSON)  # Array of execution step logs
    created_by = Column(String, nullable=True)  # User ID who created this instance
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="workflow_instances")
    execution_steps = relationship("WorkflowExecutionStep", back_populates="workflow_instance")


class WorkflowExecutionStep(Base):
    """Individual step execution within a workflow"""
    __tablename__ = "workflow_execution_steps"
    
    id = Column(String, primary_key=True)
    workflow_instance_id = Column(String, ForeignKey("workflow_instances.id"))
    step_name = Column(String(255), nullable=False)
    step_type = Column(String(100))  # ollama, openai, claude, transform, etc.
    node_id = Column(String(100))  # ID from the frontend node
    status = Column(String(50))  # pending, running, completed, failed, skipped
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    retry_count = Column(Integer, default=0)
    
    # Enhanced logging fields
    log_level = Column(String(20), default="INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    component_version = Column(String(50))  # Version of the component used
    user_id = Column(String(100))  # User who triggered the workflow
    tags = Column(JSON)  # Custom tags for categorization
    metrics = Column(JSON)  # Performance metrics (memory, CPU, etc.)
    dependencies = Column(JSON)  # What this step depends on
    artifacts = Column(JSON)  # Generated artifacts (files, URLs, etc.)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="execution_steps")
    task_logs = relationship("WorkflowTaskLog", back_populates="execution_step")


class WorkflowTaskLog(Base):
    """Enhanced logs for workflow tasks with detailed success/failure tracking"""
    __tablename__ = "workflow_task_logs"
    
    id = Column(String, primary_key=True)
    execution_step_id = Column(String, ForeignKey("workflow_execution_steps.id"))
    workflow_instance_id = Column(String, ForeignKey("workflow_instances.id"))
    
    # Core task information
    task_id = Column(String(100))  # Unique identifier for each task
    task_name = Column(String(255), nullable=False)
    task_type = Column(String(100))  # Type of task (AI processing, Google Sheets, etc.)
    
    # Execution details
    status = Column(String(50))  # pending, processing, success, failed, cancelled
    log_level = Column(String(20), default="INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Input/Output tracking
    input_data = Column(JSON)  # What was fed into the task
    output_data = Column(JSON)  # What the task produced
    expected_output = Column(JSON)  # What we expected to get
    
    # Success/Failure details
    success_criteria = Column(JSON)  # What defines success for this task
    failure_reason = Column(Text)  # Detailed failure explanation
    error_code = Column(String(50))  # Standardized error code
    error_stack_trace = Column(Text)  # Full stack trace for debugging
    
    # Performance metrics
    processing_time_ms = Column(Integer)
    memory_usage_mb = Column(Float)
    cpu_usage_percent = Column(Float)
    
    # External integrations
    sheet_id = Column(String(255))  # Google Sheets ID (if applicable)
    row_number = Column(Integer)  # Row number in the sheet (if applicable)
    api_endpoint = Column(String(500))  # External API called (if applicable)
    api_response_code = Column(Integer)  # HTTP response code (if applicable)
    
    # Notification tracking
    email_notification_sent = Column(Boolean, default=False)
    slack_notification_sent = Column(Boolean, default=False)
    webhook_notification_sent = Column(Boolean, default=False)
    
    # Metadata
    user_id = Column(String(100))  # User who triggered this task
    session_id = Column(String(100))  # Session identifier
    correlation_id = Column(String(100))  # For tracing across services
    tags = Column(JSON)  # Custom tags for categorization
    context = Column(JSON)  # Additional context information
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    execution_step = relationship("WorkflowExecutionStep", back_populates="task_logs")
    workflow_instance = relationship("WorkflowInstance")
    
    
class WorkflowDailyReport(Base):
    """Daily analytics reports"""
    __tablename__ = "workflow_daily_reports"
    
    id = Column(String, primary_key=True)
    report_date = Column(DateTime(timezone=True), nullable=False)
    total_tasks = Column(Integer, default=0)
    successful_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    success_rate = Column(String(10))  # Percentage as string
    error_breakdown = Column(JSON)  # Breakdown of error types
    analytics_chart_url = Column(String(500))  # URL to generated chart
    report_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
