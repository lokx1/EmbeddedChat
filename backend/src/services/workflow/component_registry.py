"""
Workflow Component Registry
"""
from typing import Dict, List, Type
from abc import ABC, abstractmethod
import asyncio
import time
import json

from ...schemas.workflow_components import (
    WorkflowComponentMetadata, 
    ExecutionContext, 
    ExecutionResult,
    ComponentCategory,
    ComponentParameter,
    ComponentHandle,
    ParameterType
)


class BaseWorkflowComponent(ABC):
    """Base class for all workflow components"""
    
    @classmethod
    @abstractmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        """Return component metadata"""
        pass
    
    @abstractmethod
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute the component with given context"""
        pass
    
    def validate_parameters(self, parameters: Dict) -> List[str]:
        """Validate component parameters, return list of errors"""
        errors = []
        metadata = self.get_metadata()
        
        for param in metadata.parameters:
            if param.required and param.name not in parameters:
                errors.append(f"Required parameter '{param.name}' is missing")
            
            if param.name in parameters:
                value = parameters[param.name]
                if param.type == ParameterType.NUMBER and not isinstance(value, (int, float)):
                    errors.append(f"Parameter '{param.name}' must be a number")
                elif param.type == ParameterType.BOOLEAN and not isinstance(value, bool):
                    errors.append(f"Parameter '{param.name}' must be a boolean")
        
        return errors


# Example Components

class ManualTriggerComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="manual_trigger",
            name="Manual Trigger",
            description="Manually trigger workflow execution",
            category=ComponentCategory.TRIGGERS,
            icon="PlayIcon",
            color="from-emerald-500 via-emerald-600 to-teal-600",
            parameters=[
                ComponentParameter(
                    name="trigger_data",
                    label="Trigger Data",
                    type=ParameterType.JSON,
                    description="Data to pass to the workflow"
                )
            ],
            input_handles=[],
            output_handles=[
                ComponentHandle(id="output", type="source", position="right", label="Start")
            ],
            is_trigger=True
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            # Manual trigger just passes through the trigger data
            output_data = context.input_data.get("trigger_data", {})
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data=output_data,
                execution_time_ms=execution_time,
                logs=["Manual trigger executed successfully"],
                next_steps=["output"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Error in manual trigger: {str(e)}"]
            )


class HttpRequestComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="http_request",
            name="HTTP Request",
            description="Make HTTP requests to external APIs",
            category=ComponentCategory.DATA_SOURCES,
            icon="GlobeAltIcon",
            color="from-sky-500 via-blue-600 to-indigo-600",
            parameters=[
                ComponentParameter(
                    name="url",
                    label="URL",
                    type=ParameterType.STRING,
                    required=True,
                    description="The URL to send the request to"
                ),
                ComponentParameter(
                    name="method",
                    label="HTTP Method",
                    type=ParameterType.SELECT,
                    required=True,
                    default_value="GET",
                    options=[
                        {"label": "GET", "value": "GET"},
                        {"label": "POST", "value": "POST"},
                        {"label": "PUT", "value": "PUT"},
                        {"label": "DELETE", "value": "DELETE"}
                    ]
                ),
                ComponentParameter(
                    name="headers",
                    label="Headers",
                    type=ParameterType.JSON,
                    description="HTTP headers as JSON object"
                ),
                ComponentParameter(
                    name="body",
                    label="Request Body",
                    type=ParameterType.TEXTAREA,
                    description="Request body (for POST/PUT requests)"
                ),
                ComponentParameter(
                    name="timeout",
                    label="Timeout (seconds)",
                    type=ParameterType.NUMBER,
                    default_value=30
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="success", type="source", position="right", label="Success"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ],
            is_async=True,
            max_runtime_seconds=60
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        import aiohttp
        start_time = time.time()
        
        try:
            url = context.input_data.get("url")
            method = context.input_data.get("method", "GET")
            headers = context.input_data.get("headers", {})
            body = context.input_data.get("body")
            timeout = context.input_data.get("timeout", 30)
            
            if isinstance(headers, str):
                headers = json.loads(headers)
            
            async with aiohttp.ClientSession() as session:
                kwargs = {
                    "timeout": aiohttp.ClientTimeout(total=timeout)
                }
                
                if headers:
                    kwargs["headers"] = headers
                
                if body and method in ["POST", "PUT"]:
                    kwargs["data"] = body
                
                async with session.request(method, url, **kwargs) as response:
                    response_data = {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "body": await response.text()
                    }
                    
                    try:
                        response_data["json"] = await response.json()
                    except:
                        pass
                    
                    execution_time = int((time.time() - start_time) * 1000)
                    
                    next_step = "success" if response.status < 400 else "error"
                    
                    return ExecutionResult(
                        success=response.status < 400,
                        output_data=response_data,
                        execution_time_ms=execution_time,
                        logs=[f"HTTP {method} request to {url} completed with status {response.status}"],
                        next_steps=[next_step]
                    )
                    
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Error in HTTP request: {str(e)}"],
                next_steps=["error"]
            )


class DataTransformComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="data_transform",
            name="Data Transform",
            description="Transform and manipulate data using JavaScript",
            category=ComponentCategory.AI_PROCESSING,
            icon="ArrowsRightLeftIcon",
            color="from-amber-500 via-orange-500 to-orange-600",
            parameters=[
                ComponentParameter(
                    name="transform_script",
                    label="Transform Script",
                    type=ParameterType.TEXTAREA,
                    required=True,
                    description="JavaScript code to transform the data. Input data is available as 'input' variable. Return the transformed data."
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="output", type="source", position="right", label="Output")
            ]
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            # This would require a JavaScript engine like PyV8 or similar
            # For now, we'll implement a simple Python-based transformation
            transform_script = context.input_data.get("transform_script", "")
            input_data = context.input_data.get("data", {})
            
            # Simple transformation (in real implementation, use a secure sandbox)
            # This is a simplified example - in production, use proper sandboxing
            output_data = {
                "transformed_data": input_data,
                "script_executed": True
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data=output_data,
                execution_time_ms=execution_time,
                logs=["Data transformation completed"],
                next_steps=["output"]
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Error in data transformation: {str(e)}"]
            )


class ComponentRegistry:
    """Registry for all workflow components"""
    
    def __init__(self):
        self._components: Dict[str, Type[BaseWorkflowComponent]] = {}
        self._register_default_components()
    
    def _register_default_components(self):
        """Register default components"""
        self.register_component(ManualTriggerComponent)
        self.register_component(HttpRequestComponent)
        self.register_component(DataTransformComponent)
        self.register_component(GoogleSheetsComponent)
        self.register_component(AIProcessingComponent)
        self.register_component(WebhookComponent)
        self.register_component(EmailSenderComponent)
        self.register_component(DatabaseWriteComponent)
    
    def register_component(self, component_class: Type[BaseWorkflowComponent]):
        """Register a component class"""
        metadata = component_class.get_metadata()
        self._components[metadata.type] = component_class
    
    def get_component(self, component_type: str) -> Type[BaseWorkflowComponent]:
        """Get a component class by type"""
        if component_type not in self._components:
            raise ValueError(f"Component type '{component_type}' not found")
        return self._components[component_type]
    
    def get_all_components(self) -> List[WorkflowComponentMetadata]:
        """Get metadata for all registered components"""
        return [cls.get_metadata() for cls in self._components.values()]
    
    def get_components_by_category(self, category: ComponentCategory) -> List[WorkflowComponentMetadata]:
        """Get components filtered by category"""
        return [
            cls.get_metadata() 
            for cls in self._components.values()
            if cls.get_metadata().category == category
        ]


class GoogleSheetsComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="google_sheets",
            name="Google Sheets",
            description="Read spreadsheet data",
            category=ComponentCategory.DATA_SOURCES,
            icon="TableCellsIcon",
            color="from-green-500 via-emerald-500 to-teal-500",
            parameters=[
                ComponentParameter(
                    name="sheet_id",
                    label="Sheet ID",
                    type=ParameterType.STRING,
                    required=True,
                    description="Google Sheets document ID"
                ),
                ComponentParameter(
                    name="sheet_name",
                    label="Sheet Name",
                    type=ParameterType.STRING,
                    required=True,
                    description="Name of the sheet tab"
                ),
                ComponentParameter(
                    name="range",
                    label="Cell Range",
                    type=ParameterType.STRING,
                    default_value="A1:Z1000",
                    description="Cell range to read (e.g., A1:Z1000)"
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="output", type="source", position="right", label="Data")
            ]
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            sheet_id = context.input_data.get("sheet_id")
            sheet_name = context.input_data.get("sheet_name")
            range_str = context.input_data.get("range", "A1:Z1000")
            
            # TODO: Implement actual Google Sheets API call
            # For now, return mock data
            mock_data = [
                ["Name", "Email", "Status"],
                ["John Doe", "john@example.com", "Active"],
                ["Jane Smith", "jane@example.com", "Pending"]
            ]
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data={"spreadsheet_data": mock_data},
                execution_time_ms=execution_time,
                logs=[f"Read data from sheet {sheet_name} range {range_str}"],
                next_steps=["output"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Error reading Google Sheets: {str(e)}"]
            )


class AIProcessingComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="ai_processing",
            name="AI Processing",
            description="OpenAI, Claude, Ollama",
            category=ComponentCategory.AI_PROCESSING,
            icon="CpuChipIcon",
            color="from-purple-500 via-purple-600 to-indigo-600",
            parameters=[
                ComponentParameter(
                    name="provider",
                    label="AI Provider",
                    type=ParameterType.SELECT,
                    required=True,
                    default_value="openai",
                    options=[
                        {"label": "OpenAI", "value": "openai"},
                        {"label": "Anthropic Claude", "value": "claude"},
                        {"label": "Ollama (Local)", "value": "ollama"}
                    ]
                ),
                ComponentParameter(
                    name="model",
                    label="Model",
                    type=ParameterType.STRING,
                    required=True,
                    default_value="gpt-4o",
                    description="AI model to use (e.g., gpt-4o, claude-3-5-sonnet, llama3.2)"
                ),
                ComponentParameter(
                    name="prompt",
                    label="Prompt Template",
                    type=ParameterType.TEXTAREA,
                    required=True,
                    description="AI prompt template. Use {input} to reference input data."
                ),
                ComponentParameter(
                    name="temperature",
                    label="Temperature",
                    type=ParameterType.NUMBER,
                    default_value=0.7,
                    description="Controls randomness (0.0 to 1.0)"
                ),
                ComponentParameter(
                    name="max_tokens",
                    label="Max Tokens",
                    type=ParameterType.NUMBER,
                    default_value=1000,
                    description="Maximum number of tokens to generate"
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="output", type="source", position="right", label="Response"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ],
            is_async=True,
            max_runtime_seconds=120
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            provider = context.input_data.get("provider", "openai")
            model = context.input_data.get("model", "gpt-4o")
            prompt_template = context.input_data.get("prompt", "")
            temperature = context.input_data.get("temperature", 0.7)
            max_tokens = context.input_data.get("max_tokens", 1000)
            
            # Replace {input} in prompt with actual input data
            input_str = json.dumps(context.previous_outputs)
            prompt = prompt_template.replace("{input}", input_str)
            
            # TODO: Implement actual AI API calls
            # For now, return mock response
            mock_response = f"AI processed input using {provider}/{model}: {prompt[:100]}..."
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data={"ai_response": mock_response, "model_used": model},
                execution_time_ms=execution_time,
                logs=[f"AI processing completed with {provider}/{model}"],
                next_steps=["output"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"AI processing error: {str(e)}"],
                next_steps=["error"]
            )


class WebhookComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="webhook",
            name="Webhook",
            description="HTTP trigger",
            category=ComponentCategory.TRIGGERS,
            icon="LinkIcon",
            color="from-indigo-500 via-purple-500 to-pink-500",
            parameters=[
                ComponentParameter(
                    name="webhook_url",
                    label="Webhook URL",
                    type=ParameterType.STRING,
                    required=True,
                    description="URL endpoint to listen for webhooks"
                ),
                ComponentParameter(
                    name="method",
                    label="HTTP Method",
                    type=ParameterType.SELECT,
                    default_value="POST",
                    options=[
                        {"label": "GET", "value": "GET"},
                        {"label": "POST", "value": "POST"},
                        {"label": "PUT", "value": "PUT"}
                    ]
                ),
                ComponentParameter(
                    name="headers",
                    label="Expected Headers",
                    type=ParameterType.JSON,
                    description="Headers to validate (optional)"
                )
            ],
            input_handles=[],
            output_handles=[
                ComponentHandle(id="output", type="source", position="right", label="Webhook Data"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ],
            is_trigger=True,
            is_async=True
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            webhook_url = context.input_data.get("webhook_url")
            method = context.input_data.get("method", "POST")
            
            # TODO: Implement actual webhook listener setup
            # For now, return mock webhook data
            mock_webhook_data = {
                "timestamp": time.time(),
                "method": method,
                "headers": {"content-type": "application/json"},
                "body": {"message": "webhook received"}
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data={"webhook_data": mock_webhook_data},
                execution_time_ms=execution_time,
                logs=[f"Webhook triggered via {method} to {webhook_url}"],
                next_steps=["output"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Webhook error: {str(e)}"],
                next_steps=["error"]
            )


class EmailSenderComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="email_sender",
            name="Email Sender",
            description="Send email notifications",
            category=ComponentCategory.OUTPUT_ACTIONS,
            icon="EnvelopeIcon",
            color="from-blue-500 via-blue-600 to-cyan-600",
            parameters=[
                ComponentParameter(
                    name="to_email",
                    label="To Email",
                    type=ParameterType.STRING,
                    required=True,
                    description="Recipient email address"
                ),
                ComponentParameter(
                    name="subject",
                    label="Subject",
                    type=ParameterType.STRING,
                    required=True,
                    description="Email subject line"
                ),
                ComponentParameter(
                    name="body",
                    label="Email Body",
                    type=ParameterType.TEXTAREA,
                    required=True,
                    description="Email content. Use {input} to reference workflow data."
                ),
                ComponentParameter(
                    name="from_email",
                    label="From Email",
                    type=ParameterType.STRING,
                    description="Sender email address (optional)"
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="sent", type="source", position="right", label="Sent"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ],
            is_async=True,
            max_runtime_seconds=30
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            to_email = context.input_data.get("to_email")
            subject = context.input_data.get("subject")
            body_template = context.input_data.get("body")
            from_email = context.input_data.get("from_email", "noreply@workflow.app")
            
            # Replace {input} in body with actual input data
            input_str = json.dumps(context.previous_outputs, indent=2)
            body = body_template.replace("{input}", input_str)
            
            # TODO: Implement actual email sending
            # For now, simulate email sending
            await asyncio.sleep(1)  # Simulate sending delay
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data={
                    "email_sent": True,
                    "to": to_email,
                    "subject": subject,
                    "sent_at": time.time()
                },
                execution_time_ms=execution_time,
                logs=[f"Email sent to {to_email} with subject '{subject}'"],
                next_steps=["sent"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Email sending error: {str(e)}"],
                next_steps=["error"]
            )


class DatabaseWriteComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="database_write",
            name="Database Write",
            description="Write data to database",
            category=ComponentCategory.OUTPUT_ACTIONS,
            icon="CircleStackIcon",
            color="from-gray-500 via-gray-600 to-slate-600",
            parameters=[
                ComponentParameter(
                    name="table_name",
                    label="Table Name",
                    type=ParameterType.STRING,
                    required=True,
                    description="Database table to write to"
                ),
                ComponentParameter(
                    name="operation",
                    label="Operation",
                    type=ParameterType.SELECT,
                    default_value="insert",
                    options=[
                        {"label": "Insert", "value": "insert"},
                        {"label": "Update", "value": "update"},
                        {"label": "Upsert", "value": "upsert"}
                    ]
                ),
                ComponentParameter(
                    name="data_mapping",
                    label="Data Mapping",
                    type=ParameterType.JSON,
                    required=True,
                    description="JSON mapping of workflow data to database columns"
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="success", type="source", position="right", label="Success"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ],
            is_async=True,
            max_runtime_seconds=30
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            table_name = context.input_data.get("table_name")
            operation = context.input_data.get("operation", "insert")
            data_mapping = context.input_data.get("data_mapping", {})
            
            # TODO: Implement actual database writing
            # For now, simulate database operation
            await asyncio.sleep(0.5)  # Simulate DB operation delay
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data={
                    "operation": operation,
                    "table": table_name,
                    "rows_affected": 1,
                    "timestamp": time.time()
                },
                execution_time_ms=execution_time,
                logs=[f"Database {operation} completed on table {table_name}"],
                next_steps=["success"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Database operation error: {str(e)}"],
                next_steps=["error"]
            )


# Global component registry instance
component_registry = ComponentRegistry()
