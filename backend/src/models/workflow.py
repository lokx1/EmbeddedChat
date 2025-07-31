from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, Integer, ForeignKey
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="execution_steps")


class WorkflowTaskLog(Base):
    """Logs for the Google Sheets automation tasks"""
    __tablename__ = "workflow_task_logs"
    
    id = Column(String, primary_key=True)
    task_id = Column(String(100), unique=True)  # Unique identifier for each task
    sheet_id = Column(String(255))  # Google Sheets ID
    row_number = Column(Integer)  # Row number in the sheet
    input_description = Column(Text)
    input_asset_urls = Column(JSON)  # Array of URLs
    output_format = Column(String(50))  # PNG, JPG, GIF, MP3
    model_specification = Column(String(100))  # OpenAI, Claude
    status = Column(String(50))  # pending, processing, success, failed
    output_file_urls = Column(JSON)  # Array of generated file URLs
    google_drive_folder_id = Column(String(255))
    error_message = Column(Text)
    processing_time_ms = Column(Integer)
    email_notification_sent = Column(Boolean, default=False)
    slack_notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    
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
