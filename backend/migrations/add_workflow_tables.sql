-- Migration: Add Workflow Tables
-- PostgreSQL version - Creates tables for workflow functionality

-- Workflow Templates Table
CREATE TABLE IF NOT EXISTS workflow_templates (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_data JSONB NOT NULL,  -- Node and edge configuration
    category VARCHAR(100),
    is_public BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),  -- User ID who created this template
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Workflow Instances Table
CREATE TABLE IF NOT EXISTS workflow_instances (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    template_id VARCHAR(255),
    workflow_data JSONB NOT NULL,  -- Current node and edge configuration
    status VARCHAR(50) DEFAULT 'draft',  -- draft, running, completed, failed, paused
    input_data JSONB,  -- Input parameters for the workflow
    output_data JSONB,  -- Final results
    error_message TEXT,
    execution_logs JSONB,  -- Array of execution step logs
    created_by VARCHAR(255),  -- User ID who created this instance
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign key constraint
    CONSTRAINT fk_workflow_instances_template_id 
        FOREIGN KEY (template_id) REFERENCES workflow_templates (id) ON DELETE SET NULL
);

-- Workflow Execution Steps Table
CREATE TABLE IF NOT EXISTS workflow_execution_steps (
    id VARCHAR(255) PRIMARY KEY,
    workflow_instance_id VARCHAR(255) NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    step_type VARCHAR(100),  -- ollama, openai, claude, transform, etc.
    node_id VARCHAR(100),  -- ID from the frontend node
    status VARCHAR(50),  -- pending, running, completed, failed, skipped
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    execution_time_ms INTEGER,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign key constraint
    CONSTRAINT fk_workflow_execution_steps_instance_id 
        FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances (id) ON DELETE CASCADE
);

-- Workflow Task Logs Table
CREATE TABLE IF NOT EXISTS workflow_task_logs (
    id VARCHAR(255) PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE,  -- Unique identifier for each task
    sheet_id VARCHAR(255),  -- Google Sheets ID
    row_number INTEGER,  -- Row number in the sheet
    input_description TEXT,
    input_asset_urls JSONB,  -- Array of URLs
    output_format VARCHAR(50),  -- PNG, JPG, GIF, MP3
    model_specification VARCHAR(100),  -- OpenAI, Claude
    status VARCHAR(50),  -- pending, processing, success, failed
    output_file_urls JSONB,  -- Array of generated file URLs
    google_drive_folder_id VARCHAR(255),
    error_message TEXT,
    processing_time_ms INTEGER,
    email_notification_sent BOOLEAN DEFAULT FALSE,
    slack_notification_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Workflow Daily Reports Table
CREATE TABLE IF NOT EXISTS workflow_daily_reports (
    id VARCHAR(255) PRIMARY KEY,
    report_date TIMESTAMP WITH TIME ZONE NOT NULL,
    total_workflows INTEGER DEFAULT 0,
    completed_workflows INTEGER DEFAULT 0,
    failed_workflows INTEGER DEFAULT 0,
    total_execution_time_ms INTEGER DEFAULT 0,
    average_execution_time_ms INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10,4) DEFAULT 0,
    report_data JSONB,  -- Detailed analytics data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_workflow_templates_category ON workflow_templates(category);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_is_public ON workflow_templates(is_public);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_created_by ON workflow_templates(created_by);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_created_at ON workflow_templates(created_at);

CREATE INDEX IF NOT EXISTS idx_workflow_instances_template_id ON workflow_instances(template_id);
CREATE INDEX IF NOT EXISTS idx_workflow_instances_status ON workflow_instances(status);
CREATE INDEX IF NOT EXISTS idx_workflow_instances_created_by ON workflow_instances(created_by);
CREATE INDEX IF NOT EXISTS idx_workflow_instances_created_at ON workflow_instances(created_at);

CREATE INDEX IF NOT EXISTS idx_workflow_execution_steps_instance_id ON workflow_execution_steps(workflow_instance_id);
CREATE INDEX IF NOT EXISTS idx_workflow_execution_steps_status ON workflow_execution_steps(status);
CREATE INDEX IF NOT EXISTS idx_workflow_execution_steps_step_type ON workflow_execution_steps(step_type);
CREATE INDEX IF NOT EXISTS idx_workflow_execution_steps_created_at ON workflow_execution_steps(created_at);

CREATE INDEX IF NOT EXISTS idx_workflow_task_logs_task_id ON workflow_task_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_workflow_task_logs_sheet_id ON workflow_task_logs(sheet_id);
CREATE INDEX IF NOT EXISTS idx_workflow_task_logs_status ON workflow_task_logs(status);
CREATE INDEX IF NOT EXISTS idx_workflow_task_logs_created_at ON workflow_task_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_workflow_daily_reports_report_date ON workflow_daily_reports(report_date);

-- PostgreSQL Function for updating workflow template timestamp
CREATE OR REPLACE FUNCTION update_workflow_template_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- PostgreSQL Function for updating workflow instance timestamp
CREATE OR REPLACE FUNCTION update_workflow_instance_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER trigger_update_workflow_template_updated_at
    BEFORE UPDATE ON workflow_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_workflow_template_updated_at();

CREATE TRIGGER trigger_update_workflow_instance_updated_at
    BEFORE UPDATE ON workflow_instances
    FOR EACH ROW
    EXECUTE FUNCTION update_workflow_instance_updated_at();
